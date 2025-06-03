from django.db import models
from agenda.models import Appointment

class Conversation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    dialogue = models.TextField(blank=True, null=True)
    processed_dialogue = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)