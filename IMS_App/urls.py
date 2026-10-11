from django.urls import path
from . import views


urlpatterns = [
    path('', views.print_list, name='print_list'),
    path('add/', views.add_print_job, name='add_print_job'),
    path(
        'edit/<int:job_id>/',
        views.edit_print_job,
        name='edit_print_job'
    ),
    path(
        'delete/<int:job_id>/',
        views.delete_print_job,
        name='delete_print_job'
    ),
]