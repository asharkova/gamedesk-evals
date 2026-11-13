import unittest
from unittest.mock import patch

import evaluate
from server import ChatError


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": "TC-X", "category": "normal", "question": "Question", "decision": "clarify", "rule_ids": ["APP-01"]}
        self.answer = {"decision": "clarify", "rule_ids": ["APP-01"], "answer": "When did you buy it?"}
        self.dataset = {"version": "test", "base_facts": "Synthetic facts", "cases": [self.case, {**self.case, "id": "TC-Y"}]}

    def test_matching_checks_do_not_claim_full_quality(self):
        result = evaluate.check_answer(self.case, self.answer)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["human_review_required"])

    def test_wrong_decision_is_a_mismatch(self):
        result = evaluate.check_answer(self.case, {**self.answer, "decision": "out_of_scope"})
        self.assertEqual(result["status"], "mismatch")
        self.assertFalse(result["checks"]["decision_matches"])

    def test_missing_required_reference_is_a_mismatch(self):
        result = evaluate.check_answer(self.case, {**self.answer, "rule_ids": ["PS-01"]})
        self.assertEqual(result["missing_references"], ["APP-01"])
        self.assertEqual(result["status"], "mismatch")

    def test_extra_relevant_references_are_allowed(self):
        result = evaluate.check_answer(self.case, {**self.answer, "rule_ids": ["APP-01", "PS-01"]})
        self.assertEqual(result["status"], "pass")

    @patch("evaluate.generate_answer")
    def test_only_question_and_context_reach_generation(self, mocked):
        mocked.return_value = self.answer
        configuration = {"model": "test-model", "key": "test-secret"}
        report = evaluate.run_evaluation(self.dataset, {"version": "test"}, configuration, limit=1, interval=0)
        mocked.assert_called_once_with("Question", "Synthetic facts", configuration, {"version": "test"})
        self.assertEqual(report["summary"]["pass"], 1)
        self.assertNotIn("key", report)

    @patch("evaluate.generate_answer")
    def test_case_context_overrides_default_purchase_facts(self, mocked):
        mocked.return_value = self.answer
        self.dataset["cases"][0]["scenario_context"] = "Account region is unknown"
        report = evaluate.run_evaluation(self.dataset, {"version": "test"}, {"model": "test-model"}, limit=1, interval=0)
        self.assertEqual(mocked.call_args.args[1], "Account region is unknown")
        self.assertEqual(report["cases"][0]["scenario_context"], "Account region is unknown")

    @patch("evaluate.generate_answer")
    def test_rate_limit_stops_suite_without_false_passes(self, mocked):
        mocked.side_effect = ChatError("Free-tier limit reached.", 429)
        report = evaluate.run_evaluation(self.dataset, {"version": "test"}, {"model": "test-model"}, interval=0)
        self.assertEqual(report["summary"]["error"], 1)
        self.assertEqual(report["summary"]["not_run"], 1)
        self.assertEqual(report["summary"]["pass"], 0)
        self.assertEqual(mocked.call_count, 1)


if __name__ == "__main__":
    unittest.main()
