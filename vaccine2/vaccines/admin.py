from django.contrib import admin
from .models import *

admin.site.register([Appointment, Vaccine, ConfirmationEmail, User, HealthCenter])
