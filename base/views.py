from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required  

from .forms import CustomRegistrationForm, AppointmentForm
from .models import Appointment

from chat.urls import urlpatterns
from chat.models import Room, Message

def dashboard(request):
    user = request.user
    Appointment.cancel_past_pending_appointments()

    if user.role == 'admin':
        appointments = Appointment.objects.all()  # El administrador ve todas las citas
    elif user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor__user=user)  # Los doctores solo ven sus citas
    elif user.role == 'patient':
        appointments = Appointment.objects.filter(patient__user=user)  # Los pacientes solo ven sus citas
    else:
        appointments = Appointment.objects.none()  # Si no hay un rol definido, no se muestran citas

    pending_appointments = appointments.filter(status='pending')  # Filtrar solo citas pendientes

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
                return render(request, 'dashboard.html', context)
            
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

    # Include the form in the context for rendering the page
    context['form'] = form

    return render(request, 'dashboard.html', context)

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save() 
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomRegistrationForm()

    return render(request, 'sign-up.html', {'form': form})

def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard') 
        else:
            messages.error(request, 'Invalid username or password', extra_tags='alert alert-danger text-center')
            return render(request, 'sign-in.html')
    else:
        if len(request.META["QUERY_STRING"]) > 0:
            messages.error(request, 'You need to log in first', extra_tags='alert alert-danger text-center')
        
        return render(request, 'sign-in.html')

def signout(request):
    logout(request)  
    return redirect('sign-in')

def profile(request):
    return render(request, 'profile.html')