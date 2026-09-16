import csv
import io
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from .pricing import PAISA, Tier, money

_CURRENCY = re.compile(r"[₹$€£\s]")

def parse_price(raw):
    if raw is None or not str(raw).strip():
        raise ValueError("blank price")
    value = str(raw).strip().replace(',', '')
    value = _CURRENCY.sub('', value)
    try:
        amount = Decimal(value).quantize(PAISA, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError("invalid price")
    if amount < 0:
        raise ValueError("negative price")
    return amount

def import_price_list(text, available_seats=None):
    """Import a two-column CSV: seat class, price. First valid occurrence wins."""
    available_seats = available_seats or {}
    imported, deduplicated, rejected = [], [], []
    seen = set()
    reader = csv.reader(io.StringIO(text or ""))
    for line_no, row in enumerate(reader, 1):
        if not row or all(not str(x).strip() for x in row):
            continue
        if len(row) < 2:
            rejected.append({"line": line_no, "value": ', '.join(row), "reason": "missing price"})
            continue
        name = str(row[0]).strip()
        if not name:
            rejected.append({"line": line_no, "value": ', '.join(row), "reason": "blank seat class"})
            continue
        key = name.casefold()
        try:
            price = parse_price(",".join(row[1:]))
        except ValueError as exc:
            rejected.append({"line": line_no, "value": ', '.join(row), "reason": str(exc)})
            continue
        if key in seen:
            deduplicated.append({"line": line_no, "name": name, "reason": "duplicate seat class (case-insensitive)"})
            continue
        seen.add(key)
        canonical = name.title()
        imported.append({"name": canonical, "price": price, "source_line": line_no})

    tiers = {item["name"].lower(): Tier(item["name"], item["price"], int(available_seats.get(item["name"].lower(), 20))) for item in imported}
    return {"tiers": tiers, "imported": imported, "deduplicated": deduplicated, "rejected": rejected}
