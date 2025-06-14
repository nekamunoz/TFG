from django.shortcuts import render, get_object_or_404

from core.models import Doctor
from ..models import Agenda
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

