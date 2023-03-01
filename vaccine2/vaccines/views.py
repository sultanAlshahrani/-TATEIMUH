from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .forms import CreateUserForm
from .models import Vaccine, Appointment, ConfirmationEmail, User, HealthCenter
from .tasks import send_confirmation_email, send_center_email


def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('vaccines:vaccine_list')
            else:
                messages.error(request, 'اسم المستخدم او كلمة المرور غير صحيحة')

            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('vaccines:vaccine_list')
        else:
            print(form.errors)
            messages.error(request, 'يوجد خطأ في البيانات المدخلة, يرجى المحاولة مرى اخرى')

    else:
        form = CreateUserForm()

    return render(request, 'accounts/registration.html', {
        'form': form,
    })


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('vaccines:vaccine_list')
            else:
                messages.error(request, 'اسم المستخدم او كلمة المرور غير صحيحة')
        else:
            messages.error(request, 'اسم المستخدم او كلمة المرور غير صحيحة')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('vaccines:vaccine_list')


@login_required
def vaccine_list(request):
    user = get_object_or_404(User, pk=request.user.id)
    vaccines = Vaccine.objects.exclude(pk__in=user.previous_vaccinations.all().values_list('pk', flat=True))
    return render(request, 'vaccines/vaccine_list.html', {'vaccines': vaccines})


@login_required
def book_appointment(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, pk=vaccine_id)
    user = get_object_or_404(User, pk=request.user.id)
    health_centers = HealthCenter.objects.all()
    if request.method == 'POST':
        date = request.POST['date']
        email = request.POST['email']
        health_center_id = request.POST['health_center']
        health_center = get_object_or_404(HealthCenter, pk=health_center_id)
        try:
            appointment = Appointment.objects.get(vaccine=vaccine, date=date, father=user)
            messages.error(request, 'لقد قمت بالفعل بالتسجيل لتلقي هذا اللقاح')
            return HttpResponseRedirect(reverse('vaccines:appointment_confirmation', args=(vaccine_id, date)))
        except Appointment.DoesNotExist:
            try:
                appointment = Appointment.objects.create(vaccine=vaccine, date=date, father=user, email=email,
                                                         health_center=health_center)
                confirmation_email = ConfirmationEmail.objects.create(appointment=appointment)
                send_confirmation_email.delay(appointment.id)
                user.previous_vaccinations.add(vaccine)
            except MultipleObjectsReturned:
                appointments = Appointment.objects.filter(vaccine=vaccine, date=date, father=user)
                appointments.delete()
                appointment = Appointment.objects.create(vaccine=vaccine, date=date, father=user, email=email)
                confirmation_email = ConfirmationEmail.objects.create(appointment=appointment)
                send_confirmation_email.delay(appointment.id)
                user.previous_vaccinations.add(vaccine)
        return HttpResponseRedirect(reverse('vaccines:appointment_confirmation', args=(vaccine_id, date)))
    return render(request, 'vaccines/book_appointment.html', {'vaccine': vaccine, 'health_centers': health_centers})


def appointment_confirmation(request, vaccine_id, date):
    appointment = get_object_or_404(Appointment, vaccine__id=vaccine_id, date=date)
    confirmation_email = get_object_or_404(ConfirmationEmail, appointment=appointment)
    return render(request, 'vaccines/appointment_confirmation.html',
                  {'appointment': appointment, 'confirmation_email': confirmation_email})


def vaccine_detail(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, pk=vaccine_id)
    context = {'vaccine': vaccine}
    return render(request, 'vaccines/vaccine_detail.html', context)


def health_centers_list(request):
    centers = HealthCenter.objects.all()
    context = {'centers': centers}
    return render(request, 'vaccines/health_centers_list.html', context)


def send_email(request, center_id):
    center = get_object_or_404(HealthCenter, id=center_id)
    if request.method == 'POST':
        subject = request.POST['subject']
        message = request.POST['message']
        sender = request.user.email
        recipient = center.email
        send_center_email.delay(subject, message, sender, recipient)
        messages.success(request, 'لقد تم تلقي استفسارك سيتم التواصل معك في اقرب وقت')
        return render(request, 'vaccines/email_sent.html', {'center': center})
    return render(request, 'vaccines/email_sent.html', {'center': center})
