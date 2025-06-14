from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

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