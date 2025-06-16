from django.shortcuts import render, redirect

from ..appointment.models import Appointment

def user_dashboard(request, user):
    if not user.is_authenticated:
        return None, 'redirect'
    if user.role == 'patient':
        appointments = Appointment.objects.filter(patient__user=user)
        template = 'patients_dashboard.html'
    elif user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor__user=user)  
        template = 'doctors_dashboard.html'
    elif user.role == 'admin':
        appointments = Appointment.objects.all()
        template = 'doctors_dashboard.html'
    else:
        appointments = Appointment.objects.none()
        template = 'dashboard.html'
    return appointments, template

def dashboard(request):
    user = request.user
    Appointment.cancel_past_pending_appointments()
    Appointment.finish_past_confirmed_appointments()

    appointments, template = user_dashboard(request, user)

    if template == 'redirect':
        return redirect('sign-in')

    pending_appointments = appointments.filter(status='pending', replaces_appointment__isnull=True)
    replacement_appointments = appointments.filter(status='replacement', replaces_appointment__isnull=False)

    context = {
        'appointments': appointments.order_by('date'),
        'pending_appointments': pending_appointments,
        'replacement_appointments': replacement_appointments,
    }
        
    return render(request, template, context)

from config.config import serverIp, port

def videochat(request, appointment_id=None):
    print(f"Joining room: {appointment_id} by user {request.user}")
    return render(request, 'videochat.html', {'room_id': appointment_id, 'serverIp': serverIp, 'port': port})

def appointment_notes(request, appointment_id=None):
    appointment = Appointment.objects.get(pk=appointment_id)
    conversation = Conversation.objects.get(appointment=appointment)
    return render(request, 'appointment_notes.html', {'conversation': conversation, 'appointment': appointment})

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
from ..teleconsult.models import Conversation

@require_POST
@ensure_csrf_cookie
def save_conversation(request, appointment_id=None):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')

        if appointment_id is None:
            appointment_id = request.session.get('appointment_id', 0)

        appointment = Appointment.objects.get(pk=appointment_id)

        # Ensure only one conversation exists
        if hasattr(appointment, 'conversation'):
            return JsonResponse({
                'status': 'error',
                'message': 'This appointment already has a conversation.'
            }, status=400)

        # Create new conversation
        conversation = Conversation.objects.create(
            appointment=appointment,
            dialogue=text
        )

        return JsonResponse({'status': 'success', 'id': conversation.id})

    except Appointment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Appointment not found'}, status=404)

    except Exception as e:
        print(f"Error saving conversation: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)