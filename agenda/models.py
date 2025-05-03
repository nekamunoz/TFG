from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from base.models import Doctor, Patient

from datetime import datetime, timedelta
from django.db import models
from datetime import timedelta

class Agenda(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    weekly_schedule = models.JSONField(default=dict)
    slot_duration = models.IntegerField(default=30) 

    def __str__(self):
        return f"Agenda for {self.doctor}"

    def generate_slots(self, target_date):
        weekday = str(target_date.weekday())

        if weekday not in self.weekly_schedule:
            return [], []  # No availability for this day
        if not self.weekly_schedule[weekday]:
            return [], []

        start_time_str = self.weekly_schedule[weekday].get('start', '09:00')
        end_time_str = self.weekly_schedule[weekday].get('end', '16:00')

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        start = datetime.combine(target_date, start_time)
        end = datetime.combine(target_date, end_time)
        
        slot_delta = timedelta(minutes=self.slot_duration)

        slots = []
        while start < end:
            slots.append(start.time().strftime('%H:%M'))
            start += slot_delta

        booked_slots = Appointment.objects.filter(doctor=self.doctor, date=target_date, status__in=["confirmed", "pending"])

        return slots, booked_slots

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('replacement', 'Replacement'),
        ('finished', 'Finished'),
    ]
    PRIORITY_CHOICES = [
        (1, 'Very High'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
        (5, 'Very Low'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE) 
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(default="Not specified")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    replaces_appointment = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.doctor} - {self.patient} - {self.date} {self.time} - {self.status}'

    def clean(self):
        appointment_datetime = datetime.combine(self.date, self.time)  
        time_start = appointment_datetime - timedelta(minutes=29)  
        time_end = appointment_datetime + timedelta(minutes=29)  

        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,  
            date=self.date,  
            status__in=["confirmed", "pending"] 
        ).exclude(id=self.id) 

        for appointment in overlapping_appointments:
            existing_datetime = datetime.combine(appointment.date, appointment.time)
            if time_start <= existing_datetime <= time_end:
                raise ValidationError(f'El doctor {self.doctor} ya tiene una cita en este horario o dentro de los 30 minutos antes o después.')

        overlapping_appointments = Appointment.objects.filter(
            patient=self.patient,  
            date=self.date, 
            status__in=["confirmed", "pending"] 
        ).exclude(id=self.id)

        for appointment in overlapping_appointments:
            existing_datetime = datetime.combine(appointment.date, appointment.time)
            if time_start <= existing_datetime <= time_end:
                raise ValidationError(f'El paciente {self.patient} ya tiene una cita en este horario o dentro de los 30 minutos antes o después.')


    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)

    @staticmethod
    def cancel_past_pending_appointments():
        local_time = timezone.localtime(timezone.now())
        Appointment.objects.filter(status='pending', date__lt=local_time.date()).update(status='cancelled')

    @staticmethod
    def finish_past_confirmed_appointments():
        local_time = timezone.localtime(timezone.now())
        Appointment.objects.filter(status='confirmed', date__lt=local_time.date()).update(status='finished')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time'], 
                name='unique_doctor_appointment',
                condition=models.Q(status__in=["confirmed", "pending"])
            ),
            models.UniqueConstraint(
                fields=['patient', 'date', 'time'],
                name='unique_patient_appointment',
                condition=models.Q(status__in=["confirmed", "pending"])
            )
        ]