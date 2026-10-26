from decimal import Decimal

from django.db import migrations, models
from django.core.validators import MinValueValidator


def seed_pricing(apps, schema_editor):
    PriceRule = apps.get_model("IMS_App", "PriceRule")
    paper_rates = {
        "A4": ("2.00", "8.00"),
        "A3": ("5.00", "15.00"),
        "Letter": ("3.00", "9.00"),
        "Legal": ("3.00", "10.00"),
        "Short": ("2.00", "8.00"),
        "Long": ("3.00", "10.00"),
    }
    multipliers = {
        "Document": Decimal("1.0"),
        "Photo": Decimal("2.5"),
        "Tarpaulin": Decimal("4.0"),
    }
    for paper, (bw, colored) in paper_rates.items():
        for color, base in (
            ("Black and White", bw), ("Colored", colored)
        ):
            for print_type, multiplier in multipliers.items():
                PriceRule.objects.get_or_create(
                    print_type=print_type,
                    paper_size=paper,
                    color_mode=color,
                    defaults={
                        "unit_price": Decimal(base) * multiplier
                    },
                )


class Migration(migrations.Migration):
    dependencies = [("IMS_App", "0002_printjob_delete_product")]

    operations = [
        migrations.AlterField(
            model_name="printjob",
            name="quantity",
            field=models.IntegerField(validators=[MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name="printjob",
            name="print_status",
            field=models.CharField(
                max_length=30, default="Pending",
                choices=[
                    ("Pending", "Pending"),
                    ("Processing", "Processing"),
                    ("Ready", "Ready for Pickup"),
                    ("Completed", "Completed"),
                    ("Cancelled", "Cancelled"),
                ],
            ),
        ),
        migrations.CreateModel(
            name="PriceRule",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name="ID"
                )),
                ("print_type", models.CharField(max_length=100)),
                ("paper_size", models.CharField(max_length=50)),
                ("color_mode", models.CharField(max_length=20)),
                ("unit_price", models.DecimalField(
                    max_digits=10, decimal_places=2,
                    validators=[MinValueValidator(Decimal("0.00"))]
                )),
            ],
            options={"ordering": ["print_type", "paper_size", "color_mode"]},
        ),
        migrations.AddConstraint(
            model_name="pricerule",
            constraint=models.UniqueConstraint(
                fields=("print_type", "paper_size", "color_mode"),
                name="unique_print_price_rule",
            ),
        ),
        migrations.RunPython(
            seed_pricing, reverse_code=migrations.RunPython.noop
        ),
    ]
