from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class PrintJob(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Ready", "Ready for Pickup"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    job_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    print_type = models.CharField(max_length=100)
    paper_size = models.CharField(max_length=50)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    color_mode = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_submitted = models.DateTimeField(auto_now_add=True)
    print_status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="Pending"
    )

    def __str__(self):
        return f"{self.job_id} - {self.customer_name}"


class PriceRule(models.Model):
    """An administrator-managed price per printed item."""

    print_type = models.CharField(max_length=100)
    paper_size = models.CharField(max_length=50)
    color_mode = models.CharField(max_length=20)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        ordering = ["print_type", "paper_size", "color_mode"]
        constraints = [
            models.UniqueConstraint(
                fields=["print_type", "paper_size", "color_mode"],
                name="unique_print_price_rule",
            )
        ]

    def __str__(self):
        return f"{self.print_type} / {self.paper_size} / {self.color_mode}: ₱{self.unit_price}"
