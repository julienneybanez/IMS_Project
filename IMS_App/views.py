from django.shortcuts import render
from .models import PrintJob
# Create your views here.
def print_list(request):
    print_jobs = PrintJob.objects.all()

    context = {
        'print_jobs': print_jobs
    }
    return render(request, 'PrintApp/dashboard.html', context)