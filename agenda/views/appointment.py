from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import Agenda, Appointment
from base.models import Doctor, Patient
from django.contrib.auth.decorators import login_required

from . import functions

@login_required
def appointment(request):
    selected_specialty = request.GET.get('selected_specialty', '')
    selected_date = request.GET.get('selected_date', '')
    selected_date = functions.get_selected_date(selected_date)
    patients = Patient.objects.all()

    if request.user.role == 'doctor':
        specialities = Doctor.objects.values_list('specialty', flat=True).distinct()
    else:
        specialities = ['General']

    print(selected_specialty)
    available_slots = functions.get_available_slots_by_specialty(selected_specialty, selected_date)

    return render(request, 'appointment.html', {
        'specialities': specialities,
        'agenda': available_slots,
        'selected_specialty': selected_specialty,
        'selected_date': selected_date, 
        'patients': patients
    })

@login_required
def create_appointment(request):
    if request.method == "POST":
        specialty = request.POST.get("selected_specialty")
        date = request.POST.get("selected_date")
        time = request.POST.get("selected_slot")
        reason = request.POST.get("reason")
        patient = request.POST.get("patient")

        if request.user.role == "doctor":
            status = 'pending'
            patient = get_object_or_404(Patient, id=patient)
        else:
            status = 'confirmed'
            reason = specialty
            patient = get_object_or_404(Patient, user=request.user)

        if Appointment.objects.filter(patient=patient, date=date, time=time).exists():
            messages.error(request, "You already have an appointment at this time.")
            return redirect("appointment")

        available_doctors = functions.get_available_doctors_by_specialty_time(specialty, date, time)
        if not available_doctors:
            messages.error(request, "No doctor available for this slot.")
            return redirect("appointment")

        doctor = functions.select_doctor(available_doctors, date)

        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=functions.string_to_date(date),
            time=functions.string_to_time(time),
            reason=reason,
            status=status,
            specialty=specialty
        )

        messages.success(request, "Appointment successfully created!")
        return redirect("appointment_details", appointment_id=appointment.id)

    return redirect("appointment")

@login_required
def appointment_details(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    return render(request, "appointment_details.html", {"appointment": appointment})


