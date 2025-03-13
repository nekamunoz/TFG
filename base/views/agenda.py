from django.shortcuts import render
from ..models import Doctor

from agenda.models import Agenda

from datetime import datetime

def agenda(request):        
    user = request.user
    doctor = Doctor.objects.get(user=user)

    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            slots = []
    else:
        selected_date = datetime.now().date()

    try:
        doctor_agenda = Agenda.objects.get(doctor=doctor)
        slots, booked_slots_qs = doctor_agenda.generate_slots(selected_date)
        booked_slots = {
            appointment.time.strftime('%H:%M'): appointment.status
            for appointment in booked_slots_qs
        }

    except Agenda.DoesNotExist:
        doctor_agenda = None
        slots = []
        booked_slots = {}

    return render(request, 'agenda.html', {
        'agenda': slots,
        'booked_agenda': booked_slots,
        'selected_date': selected_date
    })