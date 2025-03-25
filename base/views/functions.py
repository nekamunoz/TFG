from agenda.models import Appointment
from django.db.models import Q


def find_later_confirmed_appointments(appointment):
    """Finds the first later confirmed appointment and creates a replacement."""
    later_appointments = Appointment.objects.filter(
                doctor=appointment.doctor,
                status="confirmed"
            ).filter(
                Q(date__gt=appointment.date) | Q(date=appointment.date, time__gt=appointment.time)
            ).order_by('priority', 'date', 'time')

    if later_appointments.exists():
        later_appointment = later_appointments.first()

        new_appointment = Appointment.objects.create(
            doctor=appointment.doctor,
            patient=later_appointment.patient,
            date=appointment.date,
            time=appointment.time,
            reason=later_appointment.reason,
            priority=later_appointment.priority,
            status="pending",
            replaces_appointment=later_appointment
        )

        print(f"Created a new appointment replacing {later_appointment.id} for patient {appointment.patient}")
        return new_appointment 
    
    print("No later confirmed appointments found.")
    return None
