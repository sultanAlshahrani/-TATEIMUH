import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class Vaccine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    visit = models.CharField(max_length=250, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    child_name = models.CharField(max_length=100)
    dob = models.DateField(default=datetime.date.today)
    previous_vaccinations = models.ManyToManyField(Vaccine, blank=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.username


class HealthCenter(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(null=True, blank=True, max_length=23)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    father = models.ForeignKey(User, on_delete=models.CASCADE)
    health_center = models.ForeignKey(HealthCenter, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    email = models.EmailField()

    def __str__(self):
        return self.vaccine.name


class ConfirmationEmail(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.appointment.vaccine.name


