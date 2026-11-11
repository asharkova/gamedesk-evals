# GameDesk interface

A responsive interface for reviewing the project's initial scenarios and asking a hosted Groq model questions through the local Python backend. Draft references and live outputs are labelled separately. Phoenix, DeepEval, and measured quality evaluation results are not available yet.

## Run locally

From the repository root, using Python 3.10 or newer:

```sh
python3 server.py --setup-key
python3 server.py
```

Create a key at https://console.groq.com/keys using the Free plan. The setup command hides input and saves it to an ignored `.env` file with owner-only permissions. It does not enable billing. The server automatically syncs the policy data and serves the UI at http://127.0.0.1:8000. Without a key, reference mode still works. Restart after changing configuration. DM Sans loads from Google Fonts if available; system fonts work offline.

Keep the account on Free; the application cannot verify the provider's billing configuration. Current limits and model availability are listed at https://console.groq.com/docs/rate-limits. A free-limit error is shown without automatic retries or a paid fallback. The default is `openai/gpt-oss-20b`; `openai/gpt-oss-120b` is also allowed via `GROQ_MODEL`.

The hosted Sites link is still a static reference preview. It cannot reach your localhost backend. Deploying a live backend and configuring its secret is a separate step.

## Features

- Choose a scenario and display its drafted reference answer.
- Inspect supporting policy and assistant-design requirement identifiers.
- Search the complete development dataset and open cases in the workspace.
- Review official source links and distinguish policies from project requirements.
- Export the reference conversation as JSON with explicit provenance and no fabricated scores.
- Reset the session. Session data stays in memory until explicitly exported.

When a key is configured, Live AI mode accepts custom questions. Draft references remain available using the mode selector. Failed API calls show an error; the interface never silently substitutes a reference answer. Model IDs, latency, prompt and requirements versions are included in the session export. Responses are structurally checked, but this is not a quality score or proof of correct policy interpretation.

Each question is independent; earlier conversation messages are not sent. Unchanged sample questions include their synthetic base facts. Custom questions do not inherit those facts, so include the region, storefront, timing, and download status or expect clarifying questions. No expected decisions or reference answers are sent to the model. Do not submit real account details or secrets.

## Your learning work

Check each case against the official sources, improve its expected answer, and add your own scenarios. Keep a record of your review. AI assistance in drafting is not evidence that a test is correct or that an evaluation has passed.

The parent `requirements.json` and `cases.json` remain the source of truth. Run `node build.mjs` after editing them to refresh the UI data.
