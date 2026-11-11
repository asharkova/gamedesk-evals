import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import server


class ModelConnectionTests(unittest.TestCase):
    def setUp(self):
        self.requirements = json.loads((server.ROOT / "requirements.json").read_text())
        self.configuration = {"key": "test-key-not-real", "model": server.DEFAULT_MODEL}
        self.result = {"decision": "clarify", "answer": "When did you buy it?", "rule_ids": ["APP-01"]}

    def response(self, result=None, finish_reason="stop"):
        content = json.dumps({"choices": [{"message": {"content": json.dumps(result or self.result)}, "finish_reason": finish_reason}]})
        return io.BytesIO(content.encode())

    def test_expected_answers_are_not_in_model_payload(self):
        payload = server.make_payload("My question", "Synthetic context", self.requirements, server.DEFAULT_MODEL)
        self.assertEqual([message["role"] for message in payload["messages"]], ["system", "user"])
        self.assertEqual(json.loads(payload["messages"][1]["content"]), {"question": "My question", "scenario_context": "Synthetic context"})
        self.assertNotIn("TC-01", json.dumps(payload))
        self.assertNotIn("expected", json.dumps(payload))
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])

    @patch("server.urlopen")
    def test_missing_key_does_not_call_provider(self, mocked):
        with self.assertRaises(server.ChatError) as error:
            server.generate_answer("Question", "", {**self.configuration, "key": ""}, self.requirements)
        self.assertEqual(error.exception.status, 503)
        mocked.assert_not_called()

    @patch("server.urlopen")
    def test_success_records_actual_model_metadata(self, mocked):
        mocked.return_value = self.response()
        result = server.generate_answer("Question", "", self.configuration, self.requirements)
        self.assertEqual(result["answer"], self.result["answer"])
        self.assertEqual(result["model"], server.DEFAULT_MODEL)
        self.assertFalse(result["evaluation_run"])
        self.assertGreaterEqual(result["latency_ms"], 0)
        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, server.API_URL)
        self.assertNotIn(self.configuration["key"], request.data.decode())
        self.assertNotIn(self.configuration["key"], json.dumps(result))

    @patch("server.urlopen")
    def test_rate_limit_is_not_retried_or_replaced_with_reference(self, mocked):
        mocked.side_effect = HTTPError(server.API_URL, 429, "rate limited", {}, None)
        with self.assertRaises(server.ChatError) as error:
            server.generate_answer("Question", "", self.configuration, self.requirements)
        self.assertEqual(error.exception.status, 429)
        self.assertEqual(mocked.call_count, 1)

    @patch("server.urlopen")
    def test_provider_error_does_not_expose_secret(self, mocked):
        mocked.side_effect = HTTPError(server.API_URL, 401, "test-key-not-real", {}, None)
        with self.assertRaises(server.ChatError) as error:
            server.generate_answer("Question", "", self.configuration, self.requirements)
        self.assertNotIn(self.configuration["key"], str(error.exception))

    @patch("server.urlopen")
    def test_unknown_policy_reference_is_rejected(self, mocked):
        mocked.return_value = self.response({**self.result, "rule_ids": ["INVENTED-01"]})
        with self.assertRaises(server.ChatError):
            server.generate_answer("Question", "", self.configuration, self.requirements)

    @patch("server.urlopen")
    def test_truncated_response_is_rejected(self, mocked):
        mocked.return_value = self.response(finish_reason="length")
        with self.assertRaises(server.ChatError):
            server.generate_answer("Question", "", self.configuration, self.requirements)

    @patch("server.urlopen")
    def test_unsupported_model_does_not_call_provider(self, mocked):
        with self.assertRaises(server.ChatError):
            server.generate_answer("Question", "", {**self.configuration, "model": "unsupported"}, self.requirements)
        mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
