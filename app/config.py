from decimal import Decimal
from .pricing import Tier, PricingConfig

CINEMA = {
    "name": "Auriga Multiplex",
    "movie": "Friday Night Show",
    "date": "Today",
    "time": "8:30 PM",
    "screen": "Screen 3",
}

TIERS = {
    "silver": Tier("Silver", Decimal("150.00"), 18),
    "gold": Tier("Gold", Decimal("220.00"), 12),
    "recliner": Tier("Recliner", Decimal("350.00"), 0),
}

PRICING = PricingConfig(
    festival_discount=Decimal("50.00"),
    member_discount_percent=Decimal("10.00"),
    member_discount_cap=Decimal("100.00"),
    convenience_fee_per_ticket=Decimal("20.00"),
    gst_percent=Decimal("18.00"),
    max_tickets_per_booking=8,
)
