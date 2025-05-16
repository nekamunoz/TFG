from django.shortcuts import render, redirect

from chat.models import Room
from agenda.models import Appointment


def user_dashboard(request, user):
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

    appointments, template = user_dashboard(request, user)
    pending_appointments = appointments.filter(status='pending', replaces_appointment__isnull=True)
    replacement_appointments = appointments.filter(status='replacement', replaces_appointment__isnull=False)

    context = {
        'appointments': appointments.order_by('date'),
        'pending_appointments': pending_appointments,
        'replacement_appointments': replacement_appointments,
    }

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'room':
            username = request.POST['username']
            room = request.POST['room']

            get_room, created = Room.objects.get_or_create(room_name=room)
            return redirect('room', room_name=get_room.room_name, username=username)
        
    return render(request, template, context)

def videochat(request, appointment_id):
    print(f"Joining room: {appointment_id} by user {request.user}")
    return render(request, 'videochat.html', {'room_id': appointment_id})