from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .functions import find_later_confirmed_appointments

from agenda.models import Appointment

def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'pending':
        appointment.status = 'confirmed'

        if appointment.replaces_appointment:
            cancel_appointment(request, appointment.replaces_appointment.id)

        appointment.save()
        messages.success(request, "Appointment confirmed successfully!", extra_tags="success pending")
    else:
        messages.error(request, "Appointment cannot be confirmed.")

    return redirect('dashboard')

def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'pending':
        appointment.status = 'rejected'
        appointment.save()
        
        find_later_confirmed_appointments(appointment)
        messages.success(request, "Appointment rejected successfully!")
    else:
        messages.error(request, "Appointment cannot be rejected.")

    return redirect('dashboard')

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'confirmed':
        appointment.status = 'cancelled'
        appointment.save()

        find_later_confirmed_appointments(appointment)
        messages.success(request, "Appointment cancelled successfully!")
    else:
        messages.error(request, "Appointment cannot be cancelled.")

    return redirect('dashboard')

def change_priority(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == "POST":
        new_priority = request.POST.get("priority")
        if new_priority and new_priority.isdigit():
            new_priority = int(new_priority)
            if new_priority in dict(Appointment.PRIORITY_CHOICES).keys():
                appointment.priority = new_priority
                appointment.save()
                messages.success(request, "Priority changed successfully!")
            else:
                messages.error(request, "Invalid priority value.")
        else:
            messages.error(request, "Priority must be a number.")

    return redirect('dashboard')