from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import PriceRule, PrintJob


class PrintAppTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username="staff", password="password123", is_staff=True
        )
        cls.non_staff = User.objects.create_user(
            username="visitor", password="password123"
        )

    def setUp(self):
        self.client.force_login(self.staff)

    def payload(self, **overrides):
        values = {
            "customer_name": "Test Customer",
            "print_type": "Document",
            "paper_size": "A4",
            "quantity": 3,
            "color_mode": "Black and White",
            "total_price": "0.01",  # Malicious/tampered browser input ignored
            "print_status": "Pending",
        }
        values.update(overrides)
        return values

    def test_create_calculates_price_on_server(self):
        response = self.client.post(reverse("add_print_job"), self.payload())
        self.assertRedirects(response, reverse("print_list"))
        job = PrintJob.objects.get(customer_name="Test Customer")
        self.assertEqual(job.total_price, Decimal("6.00"))

    def test_edit_recalculates_on_quantity_change(self):
        job = PrintJob.objects.create(
            customer_name="Existing", print_type="Document", paper_size="A4",
            quantity=1, color_mode="Black and White",
            total_price=Decimal("2.00"),
        )
        response = self.client.post(
            reverse("edit_print_job", args=[job.pk]),
            self.payload(quantity=4, print_status="Ready"),
        )
        self.assertRedirects(response, reverse("print_list"))
        job.refresh_from_db()
        self.assertEqual(job.total_price, Decimal("8.00"))
        self.assertEqual(job.print_status, "Ready")


    def test_status_only_edit_preserves_historical_total(self):
        job = PrintJob.objects.create(
            customer_name="Existing", print_type="Document", paper_size="A4",
            quantity=3, color_mode="Black and White",
            total_price=Decimal("1.50"), print_status="Pending",
        )
        response = self.client.post(
            reverse("edit_print_job", args=[job.pk]),
            self.payload(print_status="Completed"),
        )
        self.assertRedirects(response, reverse("print_list"))
        job.refresh_from_db()
        self.assertEqual(job.total_price, Decimal("1.50"))
        self.assertEqual(job.print_status, "Completed")

    def test_delete_only_on_post(self):
        job = PrintJob.objects.create(
            customer_name="Existing", print_type="Document", paper_size="A4",
            quantity=1, color_mode="Black and White",
            total_price=Decimal("2.00"),
        )
        url = reverse("delete_print_job", args=[job.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(PrintJob.objects.filter(pk=job.pk).exists())
        self.client.post(url)
        self.assertFalse(PrintJob.objects.filter(pk=job.pk).exists())

    def test_unknown_price_rule_requires_admin_setup(self):
        response = self.client.post(
            reverse("add_print_job"), self.payload(print_type="Unknown Type")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No price is configured")
        self.assertFalse(PrintJob.objects.exists())

    def test_price_rule_is_managed_in_database(self):
        rate = PriceRule.objects.get(
            print_type="Document", paper_size="A4",
            color_mode="Black and White"
        )
        rate.unit_price = Decimal("4.50")
        rate.save()
        self.client.post(reverse("add_print_job"), self.payload(quantity=2))
        self.assertEqual(PrintJob.objects.get().total_price, Decimal("9.00"))

    def test_dashboard_uses_actual_counts_and_revenue(self):
        PrintJob.objects.create(
            customer_name="A", print_type="Document", paper_size="A4",
            quantity=2, color_mode="Black and White",
            total_price=Decimal("4.00"), print_status="Completed",
        )
        PrintJob.objects.create(
            customer_name="B", print_type="Document", paper_size="A4",
            quantity=2, color_mode="Black and White",
            total_price=Decimal("4.00"), print_status="Processing",
        )
        response = self.client.get(reverse("print_list"))
        self.assertEqual(response.context["processing_jobs"], 1)
        self.assertEqual(response.context["completed_jobs"], 1)
        self.assertEqual(response.context["total_revenue"], Decimal("4.00"))

    def test_reports_and_csv_are_staff_only(self):
        self.assertEqual(self.client.get(reverse("reports")).status_code, 200)
        csv_response = self.client.get(reverse("export_sales_csv"))
        self.assertEqual(csv_response.status_code, 200)
        self.assertIn("text/csv", csv_response["Content-Type"])

        self.client.logout()
        for name in ("print_list", "reports", "export_sales_csv"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login/", response["Location"])

    def test_non_staff_account_cannot_sign_in(self):
        self.client.logout()
        response = self.client.post(reverse("login"), {
            "username": "visitor", "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "authorized staff")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_registers_print_jobs_and_pricing(self):
        self.assertEqual(
            self.client.get(reverse("admin:IMS_App_printjob_changelist")).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(reverse("admin:IMS_App_pricerule_changelist")).status_code,
            403,
        )
