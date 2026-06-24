# Currency Pricing Strategy

This project now treats Sinalite as a CAD-denominated supplier and converts supplier cost into a USD retail price with margin protection.

## What happens when a price is calculated

1. The app requests the raw base price from Sinalite.
2. That supplier price is treated as `PRICING_VENDOR_CURRENCY`.
3. The price is converted into `PRICING_DISPLAY_CURRENCY` using `PRICING_CAD_TO_USD_RATE`.
4. An FX protection buffer is added with `PRICING_EXCHANGE_BUFFER_PERCENT`.
5. A fixed fee can be added with `PRICING_FIXED_FEE_USD`.
6. A markup target is applied with `PRICING_MARKUP_PERCENT`.
7. A minimum absolute profit floor can be enforced with `PRICING_MINIMUM_PROFIT_USD`.
8. The final result is rounded up using `PRICING_ROUNDING_INCREMENT`.

## Formula

Base concepts:

- `vendor_cost_cad` = supplier cost from Sinalite
- `fx_rate` = CAD to USD conversion rate
- `fx_buffer` = percentage safety buffer against exchange movement
- `landed_cost` = converted cost after FX protection and fixed fee
- `margin` = target gross margin percentage

Calculation:

```text
converted_cost = vendor_cost_cad * fx_rate
buffered_cost = converted_cost * (1 + fx_buffer)
landed_cost = buffered_cost + fixed_fee
retail_price = landed_cost / (1 - margin)
final_price = round_up(retail_price, rounding_increment)
```

If `PRICING_MINIMUM_PROFIT_USD` produces a higher sell price than the margin formula, the higher value wins.

## Why this helps

- Exchange rates fluctuate, so the FX buffer protects margin.
- Margin is controlled as a policy, not guessed manually.
- The breakdown returned by the pricing API shows exactly how the final number was built.
- Cached pricing is versioned with `PRICING_POLICY_VERSION`, so pricing policy changes can invalidate old cached prices safely.

## Recommended starting values

```text
PRICING_VENDOR_CURRENCY=CAD
PRICING_DISPLAY_CURRENCY=USD
PRICING_CAD_TO_USD_RATE=0.74
PRICING_EXCHANGE_BUFFER_PERCENT=5
PRICING_MARKUP_PERCENT=30
PRICING_FIXED_FEE_USD=0
PRICING_MINIMUM_PROFIT_USD=0
PRICING_ROUNDING_INCREMENT=0.05
```

## Operational advice

- Update `PRICING_CAD_TO_USD_RATE` daily or weekly, not on every request.
- Increase `PRICING_EXCHANGE_BUFFER_PERCENT` if margin is too volatile.
- Increase `PRICING_MARKUP_PERCENT` if overall profitability is too low.
- Use `PRICING_MINIMUM_PROFIT_USD` when low-cost items still need a minimum dollar profit.
