import io
import json
import unittest
from unittest.mock import patch

import gamedesk_tracing
import gamedesk_model

try:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
except ImportError:
    TracerProvider = None


@unittest.skipIf(TracerProvider is None, "Run with .venv/bin/python for tracing checks")
class TracingTests(unittest.TestCase):
    def setUp(self):
        self.exporter = InMemorySpanExporter()
        self.provider = TracerProvider()
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.patch = patch.object(gamedesk_tracing, "_tracer", self.provider.get_tracer("test"))
        self.patch.start()
        self.requirements = json.loads((gamedesk_model.ROOT / "requirements.json").read_text())
        self.configuration = {"key": "test-secret-do-not-record", "model": gamedesk_model.DEFAULT_MODEL}

    def tearDown(self):
        self.patch.stop()
        self.provider.shutdown()

    @patch("gamedesk_model.urlopen")
    def test_success_has_prompt_answer_and_ids_without_headers_or_key(self, mocked):
        answer = {"decision": "clarify", "answer": "When did you buy it?", "rule_ids": ["APP-01"]}
        mocked.return_value = io.BytesIO(json.dumps({"choices": [{"message": {"content": json.dumps(answer)}, "finish_reason": "stop"}]}).encode())
        result = gamedesk_model.generate_answer("Test question", "Synthetic context", self.configuration, self.requirements)
        spans = self.exporter.get_finished_spans()
        self.assertEqual(len(spans), 1)
        span = spans[0]
        self.assertEqual(span.attributes["openinference.span.kind"], "LLM")
        self.assertIn("PS-01", span.attributes["llm.input_messages.0.message.content"])
        self.assertIn("Test question", span.attributes["input.value"])
        self.assertEqual(span.attributes["output.value"], answer["answer"])
        self.assertEqual(result["trace_id"], f"{span.context.trace_id:032x}")
        self.assertEqual(span.status.status_code.name, "OK")
        self.assertNotIn(self.configuration["key"], span.to_json())
        self.assertNotIn("Authorization", span.to_json())

    @patch("gamedesk_model._generate_answer")
    def test_error_records_status_without_raw_exception_or_secret(self, mocked):
        mocked.side_effect = gamedesk_model.ChatError("test-secret-do-not-record", 429)
        with self.assertRaises(gamedesk_model.ChatError):
            gamedesk_model.generate_answer("Test question", "", self.configuration, self.requirements)
        span = self.exporter.get_finished_spans()[0]
        self.assertEqual(span.status.status_code.name, "ERROR")
        self.assertEqual(span.attributes["gamedesk.error_status"], 429)
        self.assertNotIn(self.configuration["key"], span.to_json())


if __name__ == "__main__":
    unittest.main()
