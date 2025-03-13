from datetime import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm

from agenda.models import Appointment, Agenda
from base.models import CustomUser, Doctor, Patient

class CustomRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=100)

    class Meta:
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")
        model = CustomUser
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role_choice = 'patient' 
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user	
    

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'time', 'reason']

    today = datetime.now().date()
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=today)
    time = forms.ChoiceField(choices=[], required=True)
    reason = forms.CharField(widget=forms.Textarea, required=True)
