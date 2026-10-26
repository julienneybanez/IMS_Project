from django.contrib import admin
from .models import PriceRule, PrintJob


@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = (
        "job_id", "customer_name", "print_type", "paper_size",
        "quantity", "total_price", "print_status", "date_submitted",
    )
    list_display_links = ("job_id", "customer_name")
    list_editable = ("print_status",)
    list_filter = ("print_status", "paper_size", "color_mode", "date_submitted")
    search_fields = ("customer_name", "print_type")
    readonly_fields = ("date_submitted",)
    ordering = ("-date_submitted",)
    actions = ["mark_completed"]

    @admin.action(description="Mark selected jobs as Completed")
    def mark_completed(self, request, queryset):
        count = queryset.filter(
            print_status__in=["Pending", "Processing", "Ready"]
        ).update(print_status="Completed")
        self.message_user(request, f"{count} print job(s) marked completed.")


@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):
    list_display = ("print_type", "paper_size", "color_mode", "unit_price")
    list_filter = ("print_type", "paper_size", "color_mode")
    search_fields = ("print_type",)
    list_editable = ("unit_price",)


admin.site.site_header = "PaPrint Administration"
admin.site.site_title = "PaPrint Admin"
admin.site.index_title = "Print Shop Management"
