# GameDesk Evals

Independent learning project evaluating a gaming-support assistant against public PlayStation Store policies. Not affiliated with Sony or PlayStation. No account access, purchases, or refunds are performed.

## Status

Requirements, an initial evaluation dataset, and a reference-only web interface are prepared. The assistant, model integration, Phoenix tracing, and DeepEval checks are not implemented yet. The initial cases and reference answers are AI-drafted and await human review.

See `ui/README.md` to run the interface. Review the AI-drafted scenarios before using them as evaluation targets.

## Scope

Version 1 covers standard digital game and DLC refund questions for the Canadian PlayStation Store. Other regions, pre-orders, subscriptions, currencies, physical purchases, and legal-rights disputes require clarification or referral. Game titles are scenario context, not evidence of eligibility. Inputs are synthetic; never supply real account credentials.

## Sources

Reviewed November 11, 2026. These are dated paraphrases, not a continuously updated policy feed.

- S1: https://www.playstation.com/en-ca/legal/playstation-store-cancellation-policy/
- S2: https://www.playstation.com/en-ca/support/store/ps-store-refund-request/

See `requirements.json` for the distinction between source-derived policy requirements and our assistant design choices. Consult the official sources when policies change. This prototype does not determine statutory entitlements.

## Evaluation contract

The assistant will return `decision`, `answer`, and `rule_ids`. Decisions are `eligible_to_request`, `not_eligible_under_standard_policy`, `clarify`, `refer_to_support`, or `out_of_scope`. Eligibility is informational, never an approval or completed transaction.

`cases.json` contains development cases, not measured results. Expected rule identifiers are the minimum supporting references; answers may include other relevant rules. Review answers for unsupported claims even when their structured decision matches. Do not put case answers in the assistant's context.

For each run, record the model identifier, prompt version, dataset version, settings, output, latency, and reviewer judgment. Repeat selected cases and manually inspect automated judge disagreements. Reserve additional unseen cases before claiming generalization.

## Next implementation steps

1. Build a Python command-line assistant using only the requirements as policy context.
2. Validate response structure and rule identifiers with Python checks.
3. Run and manually review the development cases.
4. Connect one evaluation tool, then capture a real failure and retest a fix.

No provider or model has been selected. Hosted model calls can incur costs; local inference depends on available hardware. Keep secrets outside Git and logs.
