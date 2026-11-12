from contextlib import contextmanager
import json
import os
from pathlib import Path


_provider = None
_tracer = None


def initialize_tracing():
    global _provider, _tracer
    if os.environ.get("GAMEDESK_TRACING", "1") == "0":
        return False
    if _provider is not None:
        return True
    root = Path(__file__).resolve().parent
    os.environ.setdefault("PHOENIX_WORKING_DIR", str(root / "results" / "private" / "phoenix"))
    try:
        from phoenix.otel import register
    except ImportError:
        print("Tracing unavailable in this Python. Use .venv/bin/python to enable Phoenix tracing.")
        return False
    _provider = register(
        project_name="gamedesk", endpoint="http://127.0.0.1:6006/v1/traces",
        protocol="http/protobuf", batch=True, auto_instrument=False,
        set_global_tracer_provider=False, verbose=False,
    )
    _tracer = _provider.get_tracer("gamedesk")
    return True


def flush_traces():
    return _provider.force_flush(timeout_millis=5000) if _provider is not None else True


class ModelTrace:
    def __init__(self, span=None):
        self.span = span

    def record_output(self, result):
        if self.span is None:
            return
        self.span.set_attribute("output.value", result["answer"])
        self.span.set_attribute("output.mime_type", "text/plain")
        self.span.set_attribute("llm.output_messages.0.message.role", "assistant")
        self.span.set_attribute("llm.output_messages.0.message.content", result["answer"])
        self.span.set_attribute("gamedesk.decision", result["decision"])
        self.span.set_attribute("gamedesk.rule_ids", json.dumps(result["rule_ids"]))
        self.span.set_attribute("gamedesk.latency_ms", result["latency_ms"])

    def identifiers(self):
        if self.span is None:
            return {}
        context = self.span.get_span_context()
        return {"trace_id": f"{context.trace_id:032x}", "span_id": f"{context.span_id:016x}"}


@contextmanager
def trace_model_call(payload, prompt_version, requirements_version):
    if _tracer is None:
        yield ModelTrace()
        return
    from opentelemetry.trace import Status, StatusCode

    attributes = {
        "openinference.span.kind": "LLM", "llm.provider": "groq",
        "llm.model_name": payload["model"], "input.value": payload["messages"][-1]["content"],
        "input.mime_type": "application/json",
        "llm.invocation_parameters": json.dumps({"max_completion_tokens": payload["max_completion_tokens"]}),
        "metadata": json.dumps({"prompt_version": prompt_version, "requirements_version": requirements_version}),
    }
    for index, message in enumerate(payload["messages"]):
        attributes[f"llm.input_messages.{index}.message.role"] = message["role"]
        attributes[f"llm.input_messages.{index}.message.content"] = message["content"]
    with _tracer.start_as_current_span(
        "gamedesk.generate_answer", attributes=attributes,
        record_exception=False, set_status_on_exception=False,
    ) as span:
        try:
            yield ModelTrace(span)
        except Exception as error:
            span.set_status(Status(StatusCode.ERROR, "Model request failed"))
            span.set_attribute("error.type", type(error).__name__)
            status = getattr(error, "status", None)
            if isinstance(status, int):
                span.set_attribute("gamedesk.error_status", status)
            span.add_event("request_failed", {"exception.type": type(error).__name__})
            raise
        else:
            span.set_status(Status(StatusCode.OK))
