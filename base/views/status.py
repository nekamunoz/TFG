from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from agenda.models import Appointment

def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, "Appointment confirmed successfully!")
    else:
        messages.error(request, "Appointment cannot be confirmed.")

    return redirect('dashboard')

def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'pending':
        appointment.status = 'rejected'
        appointment.save()
        messages.success(request, "Appointment rejected successfully!")
    else:
        messages.error(request, "Appointment cannot be rejected.")

    return redirect('dashboard')

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'confirmed':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled successfully!")
    else:
        messages.error(request, "Appointment cannot be cancelled.")

    return redirect('dashboard')
