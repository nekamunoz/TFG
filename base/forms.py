from base.models import CustomUser, Appointment
from django.contrib.auth.forms import UserCreationForm
from django import forms

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
        fields = ['doctor', 'patient', 'date', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }