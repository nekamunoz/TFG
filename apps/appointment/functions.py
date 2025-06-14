from datetime import datetime

from .models import Agenda, Appointment
from ..core.models import Doctor

def string_to_time(time_str):
    """Converts a time string to a time object."""
    return datetime.strptime(time_str, '%H:%M').time()

def string_to_date(date_str):
    """Converts a date string to a date object."""
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def get_selected_date(selected_date=None):
    """Converts a date string to a date object. If no date is provided, returns current date."""
    return datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else datetime.now().date()

def get_slots_and_booked(doctor_agenda, selected_date):
    """Generates available slots and booked slots for a given date."""
    if not doctor_agenda: 
        return [], {}
    
    all_slots, appointments_qs = doctor_agenda.generate_slots(selected_date)
    booked_slots = {appointment.time.strftime('%H:%M'): appointment.status for appointment in appointments_qs}
    return all_slots, booked_slots

def get_available_slots_by_doctor(selected_doctor, selected_date):
    """Fetches available slots for a given doctor and date."""
    if not selected_doctor or not selected_date:
        return []

    agenda = Agenda.objects.filter(doctor=selected_doctor).first()

    if not agenda:
        return [] 

    available_slots = set()
    booked_slots = set()

    all_slots, appointments_qs = agenda.generate_slots(selected_date)
    if appointments_qs:
        booked_slots = {appointment.time.strftime('%H:%M') for appointment in appointments_qs}

    available_slots.update(set(all_slots) - booked_slots)

    return sorted(list(available_slots))

def get_available_slots_by_specialty(selected_specialty, selected_date):
    """Fetches available slots for a given specialty and date."""
    if not selected_specialty or not selected_date:
        return []

    doctors = Doctor.objects.filter(specialty=selected_specialty)
    agendas = Agenda.objects.filter(doctor__in=doctors)

    specialty_slots = {}
    booked_specialty_slots = {}
    available_slots = set()

    for agenda in agendas:
        slots, appointments_qs = agenda.generate_slots(selected_date)
        
        specialty_slots[agenda.doctor] = set(slots)
        booked_specialty_slots[agenda.doctor] = {
            appointment.time.strftime('%H:%M') for appointment in appointments_qs
        }

    for doctor, slots in specialty_slots.items():
        booked_slots = booked_specialty_slots.get(doctor, set())
        available_slots.update(slots - booked_slots)  
    
    return sorted(list(available_slots))


def get_available_doctors_by_specialty_time(selected_specialty, selected_date, selected_time):
    """Fetches available doctors for a given specialty, date, and time."""
    if not selected_specialty or not selected_date or not selected_time:
        return []

    doctors = Doctor.objects.filter(specialty=selected_specialty)
    selected_date = get_selected_date(selected_date)

    available_doctors = []
    for doctor in doctors:
        agenda = Agenda.objects.filter(doctor=doctor).first()

        if not agenda:
            continue 

        available_slots = get_available_slots_by_doctor(doctor, selected_date)

        appointments_qs = Appointment.objects.filter(doctor=doctor, date=selected_date, status__in=['confirmed', 'pending'])
        booked_slots = {appointment.time.strftime('%H:%M') for appointment in appointments_qs}

        if selected_time in available_slots and selected_time not in booked_slots:
            available_doctors.append(doctor)

    return available_doctors

def count_doc_appointments(doctor, date):
    """Counts the number of appointments for a given doctor, date, and time."""
    if not doctor or not date:
        return 0
    appointments_qs = Appointment.objects.filter(doctor=doctor, date=date)
    return appointments_qs.count()

def select_doctor(available_doctors, date):
    count = {}
    for doctor in available_doctors:
        sum = count_doc_appointments(doctor, date)
        count[doctor] = sum
    return min(count, key=count.get)