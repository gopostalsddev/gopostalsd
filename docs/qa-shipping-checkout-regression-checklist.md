# QA Checklist: Shipping + Checkout Regression

## Scope
Validate that shipping calculation works immediately (no browser refresh required) in both:
- Cart page shipping widget
- Checkout flow

## Preconditions
- Backend and frontend are running.
- Test account exists and can log in.
- Account has a valid shipping address (street, city, state, zip_code, country).
- Cart contains at least 1 item.

## Test Data
- User A: complete shipping address saved in account profile.
- User B: missing one required shipping field (for validation path checks).
- At least one product with quantity greater than 1 in cart.

## Execution Table
Use this table during QA execution. Update Owner, Status, and Evidence Link for each run.

| ID | Priority | Area | Test Case | Steps (Summary) | Expected Result | Owner | Status | Evidence Link | Notes |
|---|---|---|---|---|---|---|---|---|---|
| SHIP-001 | P0 | Cart | Cart shipping works on first attempt after login | Login User A, open Cart, click Calculate Shipping | Shipping options appear on first attempt; no refresh needed |  | Not Run |  |  |
| SHIP-002 | P0 | Cart | Cart shipping handles stale profile state | Logout/login User A, immediately open Cart, calculate shipping | Shipping succeeds without second click/refresh |  | Not Run |  |  |
| SHIP-003 | P1 | Cart | Cart validation for incomplete profile | Login User B, open Cart, calculate shipping | Clear missing-fields error; no silent failure |  | Not Run |  |  |
| SHIP-004 | P0 | Checkout | Checkout step sequence does not calculate shipping too early | Open Checkout, click Continue to Shipping from step 0 | Moves to shipping step; no shipping call at step 0 |  | Not Run |  |  |
| SHIP-005 | P0 | Checkout | Checkout shipping calculates before payment step | Fill/verify shipping step, click Calculate Shipping and Continue | On success, move to payment; on failure, inline error and remain on step 1 |  | Not Run |  |  |
| SHIP-006 | P0 | Checkout | No-refresh checkout flow | Fresh login, open Checkout, calculate shipping at step 1 | Works in first pass without refresh |  | Not Run |  |  |
| SHIP-007 | P0 | Session | Session continuity between cart and checkout | Add items, calculate shipping in Cart, navigate to Checkout, continue shipping | Same cart/session persists; no empty/mismatched cart |  | Not Run |  |  |
| SHIP-008 | P1 | Guardrail | Empty cart checkout guard | Navigate to Checkout with empty cart | User is redirected or blocked from checkout progression |  | Not Run |  |  |
| SHIP-009 | P1 | Resilience | API failure handling for shipping | Simulate shipping API failure in Cart and Checkout | Actionable error shown; UI remains usable; retry works after recovery |  | Not Run |  |  |

## Browser Matrix
Execute all P0 cases at minimum on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest, if available)

## Pass Criteria
- All P0 cases pass with no refresh dependency.
- Validation and failure messages are clear.
- No cart/session mismatch between Cart and Checkout.

## Status Legend
- Not Run
- Pass
- Fail
- Blocked

## Run Header Template
Fill this once per execution run:

- Environment:
- Build/commit:
- Date/time:
- QA owner:
- Backend URL:
- Frontend URL:

## Defect Log Template
Use this when a case fails:

- Case ID:
- Severity:
- Repro steps:
- Expected:
- Actual:
- Screenshot/video/log:
- Linked issue:

## Latest Run Snapshot
Update this section for standups and status reporting.

| Case ID | Priority | Result | Comment |
|---|---|---|---|
| SHIP-001 | P0 | Not Run |  |
| SHIP-002 | P0 | Not Run |  |
| SHIP-003 | P1 | Not Run |  |
| SHIP-004 | P0 | Not Run |  |
| SHIP-005 | P0 | Not Run |  |
| SHIP-006 | P0 | Not Run |  |
| SHIP-007 | P0 | Not Run |  |
| SHIP-008 | P1 | Not Run |  |
| SHIP-009 | P1 | Not Run |  |
