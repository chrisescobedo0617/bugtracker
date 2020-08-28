from django.db import models
from django.utils import timezone
from custom_user.models import MyUser

# Create your models here.

class Ticket(models.Model):
    STATUS_CHOICES = [
        ("NW", "New"),
        ("IP", "In Progress"),
        ("DN", "Done"),
        ("IN", "Invalid")
    ]
    
    title = models.CharField(max_length=50)
    description = models.TextField()
    post_date = models.DateTimeField(default=timezone.now)
    filing_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=False)
    status = models.CharField(max_length=2, default='NW', choices=STATUS_CHOICES)
    assigned = models.CharField(default='', max_length=50, blank=True, null=True)
    completed = models.CharField(max_length=50, blank=True, null=True)

    @property
    def days_active(self):
        time = timezone.now() - self.post_date 
        return time.days