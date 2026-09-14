from django.db import models

# Create your models here.
class PrintJob(models.Model):
    job_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    print_type = models.CharField(max_length=100)
    paper_size = models.CharField(max_length=50)
    quantity = models.IntegerField()
    color_mode = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_submitted = models.DateTimeField(auto_now_add=True)
    print_status = models.CharField(max_length=30, default="Pending")

    def __str__(self):
        return f"{self.job_id} - {self.customer_name}"