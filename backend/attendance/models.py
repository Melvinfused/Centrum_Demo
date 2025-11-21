from django.db import models
from api.models import CustomUser

# Create your models here.
class companyProfile(models.Model):
    company_name = models.CharField(max_length=255)
    company_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    def __str__(self):
        return self.company_name
    
class attendanceRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    companyProfile = models.ForeignKey(companyProfile, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to='attendance_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.companyProfile.company_name} - {self.check_in_time.date()}"