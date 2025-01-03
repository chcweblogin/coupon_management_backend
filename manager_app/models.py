from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class ManagerPersonalDetails(models.Model):
    manager_id = models.CharField(primary_key=True, max_length=100)
    vso_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=15, unique=True)
    email = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)  # Updated on_delete behavior
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True)  # Gender field
    image = models.ImageField(upload_to='managers/', null=True, blank=True)  # Add image field

    def __str__(self):
        return self.name
    


