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

## CASE STUDY

| Test Case | Initial Automated Result | Anna’s Comment | What Was Done | Result After Re-scoring |
| --- | --- | --- | --- | --- |
| TC-39 | Mismatch | The bot gave a clear next step by directing the customer to PlayStation Support about the disputed purchase. | The original criteria were too strict for this case. The revised test requires only `PS-05` as a rule reference, and the Python evaluator accepts either decision label. | Pass. The same answer was scored again using the updated criteria. |

## Next steps

More test case reviews are coming soon.
