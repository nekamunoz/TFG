from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from .functions import find_later_confirmed_appointments
from ..appointment.models import Appointment

def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'pending':
        appointment.status = 'confirmed'        
        appointment.save()
        messages.success(request, "Appointment confirmed successfully.", extra_tags="success pending")
            
    elif appointment.status == 'replacement':
        appointment.status = 'confirmed'

        if appointment.replaces_appointment:
            cancel_appointment(request, appointment.replaces_appointment.id)

        appointment.save()
        messages.success(request, "Appointment replaced successfully.", extra_tags="success replacement")

    else:
        if appointment.status == 'pending':
            messages.warning(request, "Appointment cannot be confirmed.", extra_tags="warning pending")
        elif appointment.status == 'replacement':
            messages.warning(request, "Appointment cannot be confirmed.", extra_tags="warning replacement")

    return redirect('dashboard')

def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'pending':
        appointment.status = 'rejected'
        appointment.save()
        
        find_later_confirmed_appointments(appointment)
        messages.success(request, "Appointment rejected.", extra_tags="success reject-pending")

    elif appointment.status == 'replacement':
        appointment.status = 'rejected'
        appointment.save()
        find_later_confirmed_appointments(appointment)
        messages.success(request, "Rejected replacement appointment.", extra_tags="success reject-replacement")
        
    else:
        if appointment.status == 'pending':
            messages.warning(request, "Appointment cannot be rejected.", extra_tags="warning reject-pending")
        elif appointment.status == 'replacement':
            messages.warning(request, "Appointment cannot be rejected.", extra_tags="warning reject-replacement")

    return redirect('dashboard')

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'confirmed':
        appointment.status = 'cancelled'
        appointment.save()

        find_later_confirmed_appointments(appointment)
        messages.success(request, "Appointment cancelled successfully.", extra_tags="success cancel")

    else:
        messages.error(request, "Appointment cannot be cancelled.", extra_tags="success cancel")

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
                messages.success(request, "Priority changed successfully.", extra_tags="success priority")
            else:
                messages.warning(request, "Invalid priority value.", extra_tags="warning priority")
        else:
            messages.warning(request, "Priority must be a number.", extra_tags="warning priority")

    return redirect('dashboard')