from celery import shared_task
from django.core.mail import send_mail
from .models import Appointment
from django.contrib import messages

@shared_task
def send_confirmation_email(appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    print('done')
    send_mail(
        'Appointment Confirmation',
        f'You have booked an appointment for {appointment.vaccine.name} on {appointment.date}.',
        'info@ksavaccine.com',
        [appointment.email],
        fail_silently=False,
    )


@shared_task
def send_center_email(subject, message, sender, recipient):
    # appointment = Appointment.objects.get(id=appointment_id)
    print('done')
    send_mail(
        subject,
        message,
        sender,
        [recipient],
        fail_silently=False,
    )
