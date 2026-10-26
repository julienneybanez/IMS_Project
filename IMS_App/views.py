import csv
from calendar import month_name
from datetime import date
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PrintJobForm, StaffLoginForm
from .models import PrintJob
from .pricing import available_rates


class StaffLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = StaffLoginForm
    redirect_authenticated_user = False


def _month_start(months_ago):
    current = timezone.localdate()
    absolute_month = current.year * 12 + current.month - 1 - months_ago
    return date(absolute_month // 12, absolute_month % 12 + 1, 1)


def monthly_sales():
    """Six actual calendar months of completed-job sales, incl. empty months."""
    first_day = _month_start(5)
    raw = (
        PrintJob.objects.filter(
            print_status="Completed", date_submitted__date__gte=first_day
        )
        .annotate(month=TruncMonth("date_submitted"))
        .values("month")
        .annotate(order_count=Count("job_id"), revenue=Sum("total_price"))
        .order_by("month")
    )
    by_month = {
        (row["month"].year, row["month"].month): row for row in raw
    }
    items = []
    for months_ago in range(5, -1, -1):
        beginning = _month_start(months_ago)
        row = by_month.get((beginning.year, beginning.month), {})
        items.append({
            "label": f"{month_name[beginning.month][:3]} {beginning.year}",
            "orders": row.get("order_count", 0),
            "revenue": row.get("revenue") or Decimal("0.00"),
        })
    largest = max((item["revenue"] for item in items), default=Decimal("0"))
    for item in items:
        item["bar_height"] = (
            max(3, round(float(item["revenue"] / largest) * 100))
            if largest else 3
        )
    return items


def dashboard_context():
    jobs = PrintJob.objects.all().order_by("-date_submitted")
    return {
        "print_jobs": jobs,
        "total_jobs": jobs.count(),
        "customer_count": jobs.values("customer_name").distinct().count(),
        "pending_jobs": jobs.filter(print_status="Pending").count(),
        "processing_jobs": jobs.filter(print_status="Processing").count(),
        "ready_jobs": jobs.filter(print_status="Ready").count(),
        "completed_jobs": jobs.filter(print_status="Completed").count(),
        "cancelled_jobs": jobs.filter(print_status="Cancelled").count(),
        "total_revenue": jobs.filter(print_status="Completed").aggregate(
            value=Sum("total_price")
        )["value"] or Decimal("0.00"),
        "monthly_sales": monthly_sales(),
    }


@staff_member_required(login_url="login")
def print_list(request):
    return render(request, "PrintApp/dashboard.html", dashboard_context())


@staff_member_required(login_url="login")
def add_print_job(request):
    form = PrintJobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("print_list")
    return render(request, "PrintApp/add_print_job.html", {
        "form": form, "pricing_rates": available_rates(),
    })


@staff_member_required(login_url="login")
def edit_print_job(request, job_id):
    job = get_object_or_404(PrintJob, job_id=job_id)
    form = PrintJobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("print_list")
    return render(request, "PrintApp/edit_print_job.html", {
        "form": form, "print_job": job, "pricing_rates": available_rates(),
    })


@staff_member_required(login_url="login")
def delete_print_job(request, job_id):
    job = get_object_or_404(PrintJob, job_id=job_id)
    if request.method == "POST":
        job.delete()
        return redirect("print_list")
    return render(request, "PrintApp/delete_print_job.html", {"print_job": job})


@staff_member_required(login_url="login")
def reports(request):
    context = dashboard_context()
    return render(request, "PrintApp/reports.html", context)


@staff_member_required(login_url="login")
def export_sales_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="paprint-sales-report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Month", "Completed orders", "Revenue (PHP)"])
    for row in monthly_sales():
        writer.writerow([row["label"], row["orders"], row["revenue"]])
    return response
