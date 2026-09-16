from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Optional

PAISA = Decimal("0.01")

def money(value) -> Decimal:
    try:
        return Decimal(str(value)).quantize(PAISA, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid monetary value: {value}") from exc

@dataclass(frozen=True)
class Tier:
    name: str
    price: Decimal
    available_seats: int

@dataclass(frozen=True)
class PricingConfig:
    festival_discount: Decimal = Decimal("50.00")
    member_discount_percent: Decimal = Decimal("10.00")
    member_discount_cap: Decimal = Decimal("100.00")
    convenience_fee_per_ticket: Decimal = Decimal("20.00")
    gst_percent: Decimal = Decimal("18.00")
    max_tickets_per_booking: int = 8

class PricingError(ValueError):
    pass

class PricingEngine:
    def __init__(self, tiers: Dict[str, Tier], config: Optional[PricingConfig] = None):
        self.tiers = {k.lower(): v for k, v in tiers.items()}
        self.config = config or PricingConfig()
        self._validate_config()

    def _validate_config(self):
        c = self.config
        if c.festival_discount < 0 or c.member_discount_cap < 0 or c.convenience_fee_per_ticket < 0:
            raise ValueError("Discounts and fees cannot be negative")
        if not Decimal("0") <= c.member_discount_percent <= Decimal("100"):
            raise ValueError("Member discount must be between 0 and 100")
        if not Decimal("0") <= c.gst_percent <= Decimal("100"):
            raise ValueError("GST must be between 0 and 100")
        if c.max_tickets_per_booking <= 0:
            raise ValueError("Maximum booking quantity must be positive")

    def calculate(self, selections: Dict[str, int], is_member: bool = False) -> dict:
        if not selections:
            raise PricingError("Select at least one ticket")

        normalized = {}
        total_quantity = 0
        ticket_subtotal = Decimal("0.00")

        for tier_name, quantity in selections.items():
            key = str(tier_name).strip().lower()
            if key not in self.tiers:
                raise PricingError(f"Unknown ticket tier: {tier_name}")
            if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
                raise PricingError("Ticket quantities must be positive whole numbers")

            tier = self.tiers[key]
            if not tier.available_seats:
                raise PricingError(f"{tier.name} is sold out")
            if quantity > tier.available_seats:
                raise PricingError(f"Only {tier.available_seats} {tier.name} seat(s) remain")

            total_quantity += quantity
            normalized[key] = quantity
            ticket_subtotal += money(tier.price) * quantity

        if total_quantity > self.config.max_tickets_per_booking:
            raise PricingError(f"Maximum {self.config.max_tickets_per_booking} tickets per booking")

        ticket_subtotal = money(ticket_subtotal)
        festival_discount = min(money(self.config.festival_discount), ticket_subtotal)
        after_festival = money(ticket_subtotal - festival_discount)

        member_discount = Decimal("0.00")
        if is_member:
            calculated = money(after_festival * self.config.member_discount_percent / Decimal("100"))
            member_discount = min(calculated, money(self.config.member_discount_cap))

        discounted_ticket_total = money(after_festival - member_discount)
        convenience_fee = money(self.config.convenience_fee_per_ticket * total_quantity)
        taxable_amount = money(discounted_ticket_total + convenience_fee)
        gst = money(taxable_amount * self.config.gst_percent / Decimal("100"))
        total = money(taxable_amount + gst)

        lines = []
        for key, qty in normalized.items():
            tier = self.tiers[key]
            lines.append({
                "tier": tier.name,
                "quantity": qty,
                "unit_price": money(tier.price),
                "amount": money(tier.price) * qty
            })

        return {
            "currency": "INR",
            "items": lines,
            "quantity": total_quantity,
            "member": bool(is_member),
            "ticket_subtotal": ticket_subtotal,
            "festival_discount": festival_discount,
            "member_discount": member_discount,
            "discounted_ticket_total": discounted_ticket_total,
            "convenience_fee": convenience_fee,
            "taxable_amount": taxable_amount,
            "gst": gst,
            "total": total,
        }

    def available_tiers(self):
        return [{
            "name": t.name,
            "price": money(t.price),
            "available_seats": t.available_seats,
            "available": t.available_seats > 0
        } for t in self.tiers.values()]
