# GameDesk Evaluation Report (Work in Progress) · Updated November 23, 2026

## EVALUATION GOAL

When someone asks GameDesk for a refund, can the bot give them a clear next step without guessing about their purchase? The evaluation covers 39 simulated support scenarios based on the Canadian PlayStation Store refund policy, from straightforward refunds to disputed in-game purchases.

## INITIAL EVALUATION RESULTS

On November 13, 2026, 39 test cases were run against Groq. The Python evaluator checked whether the model returned the expected decision and supplied all required rule IDs. Arize Phoenix recorded the responses and displayed their evaluation annotations.

| Measure | First run | Second run |
| --- | ---: | ---: |
| Expected decision matched | 29/39 | 27/39 |
| All required rule IDs present | 16/39 | 14/39 |
| Both checks passed | 12/39 | 12/39 |
| Model requests completed | 39/39 | 39/39 |

> [!NOTE]
> **INVESTIGATION IN PROGRESS**
>
> Ten cases changed from pass to mismatch or vice versa despite the identical totals. The review is looking at what changed in the answers and which checks drove the differences.

## Case study on a disputed in-game purchase

In [TC-39](../cases.json), a customer asked for refunds for a game they had played and a separate in-game purchase they disputed. The bot explained the standard refund restriction for the game and advised contacting PlayStation Support about the disputed transaction. Anna found the response useful because it gave the customer a clear next step.

The automatic result was a mismatch. The test expected `refer_to_support`, while the model's structured decision was `not_eligible_under_standard_policy`. That label reflected the answer about the base game. Two required rule IDs were also missing.

The case now accepts either decision label and requires `PS-05`, the reference for the official refund process and support. The manual review confirmed that the bot directed the customer to support for the disputed purchase specifically. The same saved answer passed both checks under the updated criteria.

## Next steps

More test case reviews are coming soon.
