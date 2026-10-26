from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("login/", views.StaffLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("", views.print_list, name="print_list"),
    path("add/", views.add_print_job, name="add_print_job"),
    path("edit/<int:job_id>/", views.edit_print_job, name="edit_print_job"),
    path("delete/<int:job_id>/", views.delete_print_job, name="delete_print_job"),
    path("reports/", views.reports, name="reports"),
    path("reports/export/", views.export_sales_csv, name="export_sales_csv"),
]
