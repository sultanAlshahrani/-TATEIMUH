from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from .models import User, Vaccine, Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'email']

    def clean_date(self):
        date = self.cleaned_data['date']
        vaccine = self.instance.vaccine
        appointments = Appointment.objects.filter(vaccine=vaccine, date=date)
        if appointments.exists():
            raise ValidationError(_('An appointment for this date already exists.'))
        return date


class CreateUserForm(forms.ModelForm):
    previous_vaccinations = forms.ModelMultipleChoiceField(
        queryset=Vaccine.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'child_name',
            'dob',
            'previous_vaccinations',
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
            user.previous_vaccinations.set(self.cleaned_data['previous_vaccinations'])
        return user

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['previous_vaccinations'].queryset = Vaccine.objects.all()
    #     self.fields['previous_vaccinations'].widget.choices = [(vaccine.id, vaccine.name) for vaccine in
    #                                                            Vaccine.objects.all()]
