from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=7, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return self.username

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}"
    
class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    birth_date = models.DateField()

    def __str__(self):
        return f"{self.user.username}"
    
class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20,
                            choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
                            default='pending')

    def __str__(self):
        return f'{self.doctor} - {self.patient} - {self.date}'
    
    @staticmethod
    def cancel_past_pending_appointments():
        local_time = timezone.localtime(timezone.now())
        Appointment.objects.filter(status='pending', date__lte=local_time).update(status='cancelled')

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'doctor':
            Doctor.objects.create(user=instance, specialty="General")  # Default specialty
        elif instance.role == 'patient':
            Patient.objects.create(user=instance, birth_date="2000-01-01")  # Default birth date
    else:
        if instance.role == 'doctor':
            if hasattr(instance, 'patient'):
                instance.patient.delete()
            if not hasattr(instance, 'doctor'):
                Doctor.objects.create(user=instance, specialty="General")
        elif instance.role == 'patient':
            if hasattr(instance, 'doctor'):
                instance.doctor.delete()
            if not hasattr(instance, 'patient'):
                Patient.objects.create(user=instance, birth_date="2000-01-01")
