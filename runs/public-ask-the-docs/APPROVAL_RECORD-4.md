# APPROVAL_RECORD-4: price confirmation and an Azure budget alert (owner's instruction, after the run)

Approver: **Gopal Patwa** (owner, in the driving session). Owner's words: "Confirm the Anthropic price and set an Azure budget alert".

Recorded at: 2026-10-23T06:47:21Z (`date -u` when recorded; the owner's message carries no timestamp).

## 1. Price confirmed (read-only)
Sources read 2026-10-23: Anthropic's pricing page and models overview. `claude-sonnet-5-5`: **$2 per million input tokens, $10 per million output tokens** (5-minute cache writes $2.50, 1-hour $4, cache reads $0.10, Batch API $1 and $5), no long-context surcharge; the id is a pinned snapshot, retirement not sooner than 2027-09-28; default effort `high`. The owner's direct API test earlier (HTTP 200 with `output_config.effort: high`) shows the effort field is accepted. **The service's built-in prices are $3 and $15**, so its spend counter overstates cost by 50% (a safe error). Recomputed from the gate's recorded tokens (71,151 in, 1,460 out): **$0.00785 per question** (the service's counter: $0.0118). Not changed: moving the service to the real price is a parameter change on redeploy (`ASK_PRICE_IN_NANO_PER_TOKEN=2000`, `ASK_PRICE_OUT_NANO_PER_TOKEN=10000`; tech spec section 7), left to the owner.

## 2. Azure budget alert (an action outside Charter v2's resource list, done on this direct instruction)
- Created: budget `bud-aveto-ask`, scope resource group `rg-aveto-ask`, **$20 a month** (amount chosen by the Orchestrator: expected cost is a few dollars, the registry's fixed fee being the largest known item; change it if you want), monthly, 2026-10-01 to 2028-10-31, category Cost.
- Notifications to the **Owner role** (one holder; no email address was entered by the run): at 50%, 80% and 100% of actual cost and at 100% of forecast cost.
- It only notifies. It does not stop or cap any spending. Charter v2 C8.3 names no budget, so it is **not in `infra/main.bicep`**; it was created by hand (`az rest` PUT, `Microsoft.Consumption/budgets`, API 2023-05-01) and is removed with the DELETE in the runbook. Read back after creation: amount 20, 4 notifications, current spend 0.
- A separate subscription budget (`compass-pilot-budget`, $100) belongs to the owner's other work and was not touched.
- Verified only that the budget exists and one Owner role holder exists at that scope; whether the notification e-mail reaches the owner's inbox was not tested (Azure sends on a threshold, which has not been crossed).
