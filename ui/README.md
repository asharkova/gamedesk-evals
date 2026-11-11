# GameDesk interface

A dependency-free, responsive interface for reviewing the project's initial scenarios. It is a reference prototype: all sample answers and cases are AI-drafted and require human review. There is no model connection, Phoenix tracing, DeepEval integration, or measured evaluation result yet.

## Run locally

From this directory:

```sh
node build.mjs
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8000. A local HTTP server is required because the interface fetches JSON data. DM Sans loads from Google Fonts if available; system fonts work offline.

## Features

- Choose a scenario and display its drafted reference answer.
- Inspect supporting policy and assistant-design requirement identifiers.
- Search the complete development dataset and open cases in the workspace.
- Review official source links and distinguish policies from project requirements.
- Export the reference conversation as JSON with explicit provenance and no fabricated scores.
- Reset the session. Session data stays in memory until explicitly exported.

Editing the question does not generate an AI response. The interface explains that a model connection is required for custom questions. It deliberately does not present canned responses as model outputs.

## Your learning work

Check each case against the official sources, improve its expected answer, and add your own scenarios. Keep a record of your review. AI assistance in drafting is not evidence that a test is correct or that an evaluation has passed.

The parent `requirements.json` and `cases.json` remain the source of truth. Run `node build.mjs` after editing them to refresh the UI data.
