"""Server-side pricing; browser estimates are for display only."""

from decimal import Decimal, ROUND_HALF_UP
from .models import PriceRule


class MissingPriceRule(Exception):
    pass


def calculate_price(print_type, paper_size, color_mode, quantity):
    rule = PriceRule.objects.filter(
        print_type__iexact=print_type.strip(),
        paper_size=paper_size,
        color_mode=color_mode,
    ).first()
    if rule is None:
        raise MissingPriceRule(
            "No price is configured for this print type, paper size, and color mode. "
            "Ask an administrator to add a Pricing Rule first."
        )
    return (rule.unit_price * Decimal(quantity)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def available_rates():
    return list(
        PriceRule.objects.values(
            "print_type", "paper_size", "color_mode", "unit_price"
        ).order_by("print_type", "paper_size", "color_mode")
    )
