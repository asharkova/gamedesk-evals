# GameDesk Evals

I’m building a small gaming-support assistant to learn how to test AI answers: catch made-up claims, handle missing information, and check whether prompt changes actually help.

The first version focuses on game and DLC refund questions using public PlayStation Store policies for Canada.

## What works so far

- A simple UI for exploring sample questions and policy references.
- 15 draft test cases covering refunds, unclear requests, and attempts to override the rules.
- A session export for reviewing example conversations.

The UI currently shows reference answers. Live AI, Phoenix tracing, and DeepEval checks are next. The initial cases and answers were drafted with AI and still need human review; no evaluation results are available yet.

## Try it locally

```sh
node ui/build.mjs
python3 -m http.server 8000 --bind 127.0.0.1 --directory ui/dist
```

Open http://127.0.0.1:8000. More details are in the [UI README](ui/README.md).

## Policy sources

Reviewed November 11, 2026:

- [PlayStation Store cancellation policy](https://www.playstation.com/en-ca/legal/playstation-store-cancellation-policy/)
- [Refund-request guide](https://www.playstation.com/en-ca/support/store/ps-store-refund-request/)

This is an independent learning project, not official PlayStation support. It cannot access accounts or issue refunds.
