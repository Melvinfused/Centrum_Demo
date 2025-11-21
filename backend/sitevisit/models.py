from django.db import models
from api.models import CustomUser

# Create your models here.
class siteProfile(models.Model):
    site_name = models.CharField(max_length=255)
    site_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.site_name
    
class sitevisitRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    siteProfile = models.ForeignKey(siteProfile, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to='sitevisit_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.siteProfile.site_name} - {self.check_in_time.date()}"