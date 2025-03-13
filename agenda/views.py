from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Agenda, Appointment
from base.models import Doctor, Patient
from django.contrib.auth.decorators import login_required

from . import functions

@login_required
def agenda(request): 
    selected_date = request.POST.get('selected_date')
    selected_date = functions.get_selected_date(selected_date)

    doctor = get_object_or_404(Doctor, user=request.user)
    doctor_agenda = Agenda.objects.filter(doctor=doctor).first()

    slots, booked_slots = functions.get_slots_and_booked(doctor_agenda, selected_date)

    return render(request, 'agenda.html', {
        'selected_date': selected_date,
        'agenda': slots,
        'booked_agenda': booked_slots
    })

@login_required
def appointment(request):
    selected_specialty = request.GET.get('selected_specialty', '')
    selected_date = request.GET.get('selected_date', '')
    selected_date = functions.get_selected_date(selected_date)

    specialities = Doctor.objects.values_list('specialty', flat=True).distinct()

    available_slots = functions.get_available_slots_by_specialty(selected_specialty, selected_date)

    return render(request, 'appointment.html', {
        'specialities': specialities,
        'agenda': available_slots,
        'selected_specialty': selected_specialty,
        'selected_date': selected_date
    })

@login_required
def create_appointment(request):
    if request.method == "POST":
        specialty = request.POST.get("selected_specialty")
        date = request.POST.get("selected_date")
        time = request.POST.get("selected_slot")
        patient = get_object_or_404(Patient, user=request.user)

        if Appointment.objects.filter(patient=patient, date=date, time=time).exists():
            messages.error(request, "You already have an appointment at this time.")
            return redirect("appointment")

        available_doctors = functions.get_available_doctors_by_specialty_time(specialty, date, time)
        if not available_doctors:
            messages.error(request, "No doctor available for this slot.")
            return redirect("appointment")

        doctor = functions.select_doctor(available_doctors, date)

        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=functions.string_to_date(date),
            time=functions.string_to_time(time),
            reason=specialty
        )

        messages.success(request, "Appointment successfully created!")
        return redirect("appointment")  

    return redirect("appointment")