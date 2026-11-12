# GameDesk Evals

I’m building a small gaming-support assistant to learn how to test AI answers: catch made-up claims, handle missing information, and check whether prompt changes actually help.

The first version focuses on game and DLC refund questions using public PlayStation Store policies for Canada.

## What works so far

- A simple UI for exploring sample questions and policy references.
- 15 draft test cases covering refunds, unclear requests, and attempts to override the rules.
- A session export for reviewing example conversations.

You can explore draft reference answers or connect a hosted Groq model through the Python backend. The initial cases and reference answers were drafted with AI and still need human review. Phoenix and DeepEval are next.

## Try it locally

```sh
python3 server.py
```

Open http://127.0.0.1:8000. More details are in the [UI README](ui/README.md).

For live answers, create a key on [Groq's Free plan](https://console.groq.com/keys), run `python3 server.py --setup-key`, then start the server again. The hidden prompt saves your key to an ignored local `.env` file. Don't share or commit it. The default model is `openai/gpt-oss-20b`; free-tier limits apply. The app cannot check your billing plan, so keep the Groq account on Free.

The interface runs locally; Groq hosts the model. Only submitted questions, optional synthetic scenario facts, and public requirements are sent to Groq. Expected answers stay out of the model prompt. Each request is independent. The existing hosted site remains a static reference preview.

Run the backend checks with `python3 -m unittest discover -s tests -v`. These use simulated API responses; a real key is needed to verify live access.

## Check real answers

Run `python3 evaluate.py --limit 3` for a small live check, or `python3 evaluate.py` for all development cases. The runner compares decisions and required rule references, then saves actual answers and results in ignored `results/private/`. It sends questions and policies, never expected answers, to Groq. Calls are spaced out; rate-limit or setup errors stop the remaining cases without retries.

A pass means those specific checks matched the draft expectation. It does not prove every sentence is correct. Review unsupported claims and confirm the expected answers yourself.

## Phoenix dashboard

Phoenix uses a separate Python 3.13 environment. To reproduce the setup, create a `.venv` with Python 3.13 and install `requirements-phoenix.txt` into it. Start the dashboard with `python3 start_phoenix.py`, then open http://127.0.0.1:6006.

Run `.venv/bin/python server.py` for traced chat or `.venv/bin/python evaluate.py --limit 3` for traced checks. Open the `gamedesk` project in Phoenix. Traces contain the question, policy prompt, answer, model, duration, and error status, but not API keys or request headers. Trace IDs are also saved in model responses and evaluation reports. Data stays in ignored `results/private/phoenix/`. Set `GAMEDESK_TRACING=0` to disable capture. Prompts and answers may contain whatever you submit, so use synthetic data.

## Policy sources

Reviewed November 11, 2026:

- [PlayStation Store cancellation policy](https://www.playstation.com/en-ca/legal/playstation-store-cancellation-policy/)
- [Refund-request guide](https://www.playstation.com/en-ca/support/store/ps-store-refund-request/)

This is an independent learning project, not official PlayStation support. It cannot access accounts or issue refunds.
