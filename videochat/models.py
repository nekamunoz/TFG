from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
from agenda.models import Appointment
from videochat.process_dialoge import summarize_medical_conversation

def process_conversation(conversation):
    try:
        if not conversation.processed_dialogue:
            if not conversation.dialogue:
                raise ValueError("The conversation dialogue is empty or None.")
            
            print(f"Processing conversation for appointment {conversation.appointment.id}")
            conversation.processed_dialogue = summarize_medical_conversation(conversation.dialogue)
            conversation.save(update_fields=['processed_dialogue'])
            print("Processing complete")
    except ValueError as ve:
        print(f"Validation error: {ve}")
        conversation.processed_dialogue = "Error: Dialogue is missing or invalid."
        conversation.save(update_fields=['processed_dialogue'])
    except Exception as e:
        print(f"Error processing conversation: {e}")
        conversation.processed_dialogue = "Error: An unexpected error occurred during processing."
        conversation.save(update_fields=['processed_dialogue'])

class Conversation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    dialogue = models.TextField(blank=True, null=True)
    processed_dialogue = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Conversation)
def auto_process_conversation(sender, instance, created, **kwargs):
    if created:
        threading.Thread(target=process_conversation, args=(instance,)).start()
