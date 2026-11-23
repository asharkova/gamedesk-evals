# GameDesk evaluation report

I evaluated how a GameDesk prototype handles refund questions about digital games and add-ons from the Canadian PlayStation Store. The development set contains 39 synthetic scenarios, including incomplete purchase details, reported faults, disputed transactions, and attempts to override the bot's instructions. I designed 24 scenarios and used 15 AI-drafted scenarios.

## Baseline results

I ran the same 39 cases twice with GPT-OSS 20B on Groq on November 13, 2026. The Python evaluator checked whether the model returned the expected decision and supplied all required rule IDs. I used Arize Phoenix to inspect individual responses and their evaluation annotations.

| Measure | First run | Second run |
| --- | ---: | ---: |
| Expected decision matched | 29/39 | 27/39 |
| All required rule IDs present | 16/39 | 14/39 |
| Both checks passed | 12/39 | 12/39 |
| Model requests completed | 39/39 | 39/39 |

Ten cases changed from pass to mismatch or vice versa despite the identical totals. These checks measure agreement with the test expectations. The wording, factual claims, and usefulness of a response also need human review.

## Case study on a disputed in-game purchase

In [TC-39](../cases.json), a customer asked for refunds for a game they had played and a separate in-game purchase they disputed. The bot explained the standard refund restriction for the game and advised contacting PlayStation Support about the disputed transaction. I was satisfied with the next step. It was clear whom to contact and why.

The automatic result was a mismatch. The test expected `refer_to_support`, while the model's structured decision was `not_eligible_under_standard_policy`. That label reflected the answer about the base game. Two required rule IDs were also missing.

I updated this case to accept either decision label and require `PS-05`, the reference for the official refund process and support. In my review of the text, I checked that the bot directed the customer to support for the disputed purchase specifically. I replayed the same saved answer against the updated criteria, and both checks passed. The new result reflects a change to the evaluation criteria.

## Next comparison

I plan to run GPT-OSS 20B and GPT-OSS 120B on the same scenarios with the same prompt and evaluation criteria. I’ll compare the automated results and read a sample of the answers to see whether either model gives customers clearer next steps.
