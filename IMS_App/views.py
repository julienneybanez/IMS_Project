from django.shortcuts import render, redirect, get_object_or_404
from .models import PrintJob
from .forms import PrintJobForm


def print_list(request):
    print_jobs = PrintJob.objects.all().order_by('-date_submitted')

    context = {
        'print_jobs': print_jobs,
        'total_jobs': print_jobs.count(),
        'customer_count': print_jobs.values('customer_name').distinct().count(),
        'pending_jobs': print_jobs.filter(print_status='Pending').count(),
    }

    return render(request, 'PrintApp/dashboard.html', context)


def add_print_job(request):
    if request.method == 'POST':
        form = PrintJobForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('print_list')
    else:
        form = PrintJobForm()

    context = {
        'form': form
    }

    return render(request, 'PrintApp/add_print_job.html', context)


def edit_print_job(request, job_id):
    print_job = get_object_or_404(PrintJob, job_id=job_id)

    if request.method == 'POST':
        form = PrintJobForm(request.POST, instance=print_job)

        if form.is_valid():
            form.save()
            return redirect('print_list')
    else:
        form = PrintJobForm(instance=print_job)

    context = {
        'form': form,
        'print_job': print_job
    }

    return render(request, 'PrintApp/edit_print_job.html', context)


def delete_print_job(request, job_id):
    print_job = get_object_or_404(PrintJob, job_id=job_id)

    if request.method == 'POST':
        print_job.delete()
        return redirect('print_list')

    context = {
        'print_job': print_job
    }

    return render(request, 'PrintApp/delete_print_job.html', context)