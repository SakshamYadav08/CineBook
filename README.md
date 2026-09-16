# Ticket Pricing Engine

A reusable multiplex counter pricing engine with a responsive booking UI, tier availability, configurable offers, accurate currency arithmetic, line-by-line billing and automated tests.

## Features

- Silver, Gold and Recliner tiers
- Inventory-aware availability and sold-out handling
- Multi-tier bookings
- Festival flat discount
- Capped member percentage discount
- Per-ticket convenience fee
- GST
- Exact paisa calculations using Python `Decimal`
- Professional responsive counter UI
- Live bill preview with color-coded discounts
- Printable receipt
- REST API
- Automated tests
- Cinema/show configuration separated from pricing logic

## Current configuration

Commercial values are configurable in `app/config.py`.

| Rule | Sample value |
|---|---:|
| Silver | ₹150.00 |
| Gold | ₹220.00 |
| Recliner | ₹350.00 |
| Festival discount | ₹50.00 |
| Member discount | 10% |
| Member discount cap | ₹100.00 |
| Convenience fee | ₹20.00/ticket |
| GST | 18% |
| Booking limit | 8 tickets |

The problem statement does not provide exact commercial values, so these are documented sample assumptions rather than claimed requirements.

## Calculation order

```text
Ticket subtotal
- Festival discount
- Member discount (capped)
+ Convenience fee
= Taxable amount
+ GST
= Grand total
```

GST is calculated on the discounted ticket total plus convenience fee. Every monetary intermediate is rounded to two decimal places using `ROUND_HALF_UP`.

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```

Open forwarded port 5000 in GitHub Codespaces.

## Test

```bash
python -m pytest -q
```

## API

### GET `/api/tiers`

Returns configured ticket tiers and available inventory.

### POST `/api/price`

Example:

```json
{
  "selections": {
    "Silver": 1,
    "Gold": 2
  },
  "member": true
}
```

The response includes ticket lines, discounts, fee, GST and final total.

## Debugging

- If imports fail, run commands from the repository root.
- Reinstall dependencies with `pip install -r requirements.txt`.
- Run `python -m pytest -q`.
- Pricing rules are isolated in `app/pricing.py`.
- Cinema-specific values are in `app/config.py`.

## Structure

```text
app/
  config.py
  pricing.py
  main.py
  templates/index.html
  static/style.css
tests/test_pricing.py
README.md
REASONING.md
AI_LOGS.md
requirements.txt
```

## Assumptions

The supplied problem statement intentionally leaves some values and ordering details open. Those choices are centralized and documented so the engine can be adapted to another cinema counter without rewriting the core pricing logic.
