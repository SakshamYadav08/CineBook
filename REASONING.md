# Reasoning

## Problem interpretation

The brief asks for a pricing engine a cinema counter can trust, not merely a single hard-coded total. The design therefore separates reusable pricing logic from cinema-specific configuration and adds a small counter UI to make the result operationally useful.

## Requirements derived from the brief

1. Different ticket tiers have different prices.
2. A tier can become unavailable/sold out.
3. A booking can contain tickets from multiple tiers.
4. A flat festival discount is applied at booking level.
5. Members receive a percentage discount subject to a cap.
6. Every ticket adds a convenience fee.
7. GST is applied after the ticket/fee calculation.
8. Currency must be accurate to the paisa.
9. The customer needs a line-by-line bill.
10. The engine should be reusable for another cinema/show.

## Design

`app/pricing.py` is the business layer. It accepts tier selections and returns a complete structured bill. It does not know anything about Flask or HTML.

`app/config.py` holds cinema/show details and commercial rules. This makes the engine configurable rather than tied to one show.

`app/main.py` exposes the engine through a small REST API and renders the counter UI.

## Money handling

Python binary floats are unsuitable for exact currency arithmetic. `Decimal` is used for all money operations and values are quantized to `0.01` with `ROUND_HALF_UP`.

## Discount and tax ordering

Because the brief does not state exact ordering, the implementation chooses and documents:

```text
subtotal
→ festival discount
→ member percentage discount with cap
→ convenience fee
→ GST
→ total
```

This gives a deterministic calculation and keeps discounts from reducing the convenience fee.

## Availability

Availability is represented by `available_seats`. The UI disables sold-out tiers, while the server independently validates inventory. This prevents a client from bypassing the rule.

## User experience

The UI uses a counter-style flow:

```text
Choose tickets → see live bill → review breakdown → print receipt
```

The live bill reduces manual arithmetic at the counter and makes each charge visible.

## Validation

The backend rejects unknown tiers, empty bookings, invalid quantities, quantities beyond inventory and bookings beyond the configured limit.

## Testing

Tests cover normal bookings, member discounts, the cap, multi-tier bookings, sold-out inventory, insufficient inventory, empty bookings, booking limits and unknown tiers.

## Scope and future production work

A production cinema would likely connect this engine to persistent seat inventory and transaction locking, authentication, a show database, audit logs and payment systems. Those are not required by the short brief, so they are intentionally not included.
