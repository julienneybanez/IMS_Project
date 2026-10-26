from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import PrintJob
from .pricing import MissingPriceRule, calculate_price


class StaffLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "This application is for authorized staff accounts only.",
                code="not_staff",
            )


class PrintJobForm(forms.ModelForm):
    PAPER_SIZE_CHOICES = [
        ("A4", "A4"),
        ("A3", "A3"),
        ("Letter", "Letter"),
        ("Legal", "Legal"),
        ("Short", "Short"),
        ("Long", "Long"),
    ]
    COLOR_MODE_CHOICES = [
        ("Black and White", "Black and White"),
        ("Colored", "Colored"),
    ]

    print_type = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. Document, Photo, Tarpaulin",
            "list": "print-type-suggestions",
        }),
    )
    paper_size = forms.ChoiceField(choices=PAPER_SIZE_CHOICES)
    color_mode = forms.ChoiceField(choices=COLOR_MODE_CHOICES)
    quantity = forms.IntegerField(
        min_value=1, widget=forms.NumberInput(attrs={
            "min": 1, "placeholder": "Enter quantity",
        })
    )
    print_status = forms.ChoiceField(
        choices=PrintJob.STATUS_CHOICES, initial="Pending"
    )
    # Display-only; incoming prices are never trusted.
    total_price = forms.DecimalField(
        required=False, disabled=True,
        widget=forms.NumberInput(attrs={
            "step": "0.01", "placeholder": "Calculated automatically"
        }),
    )

    class Meta:
        model = PrintJob
        fields = [
            "customer_name", "print_type", "paper_size", "quantity",
            "color_mode", "total_price", "print_status",
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={
                "placeholder": "Enter customer name"
            }),
        }

    def clean(self):
        data = super().clean()
        price_fields = ("print_type", "paper_size", "color_mode", "quantity")
        if any(data.get(name) in (None, "") for name in price_fields):
            return data
        # Preserve historical totals on status-only or customer-name edits.
        # New rates apply only when an order's printing specifications change.
        if self.instance.pk and all(
            data[name] == getattr(self.instance, name)
            for name in price_fields
        ):
            data["total_price"] = self.instance.total_price
            return data

        try:
            data["total_price"] = calculate_price(
                *(data[name] for name in price_fields)
            )
        except MissingPriceRule as exc:
            self.add_error("print_type", str(exc))
        return data
