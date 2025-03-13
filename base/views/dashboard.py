from django.contrib import messages
from django.shortcuts import render, redirect

from ..forms import AppointmentForm
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
    pending_appointments = appointments.filter(status='pending')  

    context = {
        'appointments': appointments.order_by('date'),
        'pending_appointments': pending_appointments,
    }

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'room':
            username = request.POST['username']
            room = request.POST['room']

            get_room, created = Room.objects.get_or_create(room_name=room)
            return redirect('room', room_name=get_room.room_name, username=username)
        
        elif action == "appointment":
            form = AppointmentForm(request.POST)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Appointment successfully created!', extra_tags='alert alert-success text-center')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid form', extra_tags='alert alert-danger text-center')
                context['form'] = form
                return render(request, template, context)
            
        elif action == "confirm":  
            appointment_ids = request.POST.getlist('appointments')  

            if appointment_ids:
                Appointment.objects.filter(id__in=appointment_ids).update(status='confirmed') 
                messages.success(request, 'Appointments confirmed successfully!', extra_tags='alert alert-success text-center')
            else:
                messages.warning(request, 'No appointments selected.', extra_tags='alert alert-warning text-center')

            return redirect('dashboard')
    else:
        form = AppointmentForm()

    context['form'] = form
    return render(request, template, context)