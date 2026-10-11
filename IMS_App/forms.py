from django import forms
from .models import PrintJob


class PrintJobForm(forms.ModelForm):
    PAPER_SIZE_CHOICES = [
        ('A4', 'A4'),
        ('A3', 'A3'),
        ('Letter', 'Letter'),
        ('Legal', 'Legal'),
        ('Short', 'Short'),
        ('Long', 'Long'),
    ]

    COLOR_MODE_CHOICES = [
        ('Black and White', 'Black and White'),
        ('Colored', 'Colored'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    paper_size = forms.ChoiceField(
        choices=PAPER_SIZE_CHOICES
    )

    color_mode = forms.ChoiceField(
        choices=COLOR_MODE_CHOICES
    )

    print_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        initial='Pending'
    )

    class Meta:
        model = PrintJob
        fields = [
            'customer_name',
            'print_type',
            'paper_size',
            'quantity',
            'color_mode',
            'total_price',
            'print_status',
        ]

        widgets = {
            'customer_name': forms.TextInput(
                attrs={
                    'placeholder': 'Enter customer name'
                }
            ),
            'print_type': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Document, Photo, Tarpaulin'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'min': 1,
                    'placeholder': 'Enter quantity'
                }
            ),
            'total_price': forms.NumberInput(
                attrs={
                    'min': 0,
                    'step': '0.01',
                    'placeholder': 'Enter total price'
                }
            ),
        }