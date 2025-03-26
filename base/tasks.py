from celery import shared_task
from django.core.mail import send_mail
from base.models import CustomUser
from agenda.models import Appointment
from datetime import timedelta
from django.utils import timezone

@shared_task()
def enviar_correo_diario():
    current_time = timezone.now()
    print(current_time)
    in_48 = current_time + timedelta(hours=48)
    appointments = Appointment.objects.filter(date__lte=in_48.date())
    count = 0
    for a in appointments:
        print(a.patient)
        print(a.patient.user)
        usuario = CustomUser.objects.get(username=a.patient.user)
        send_mail(
            "Recordatorio de Cita Médica",
            f"Hola {usuario.first_name}, le recordamos que tiene una cita médica el {str(a.date)} a las {str(a.time)}.",
            "appbio148@gmail.com",
            [usuario.email],
            fail_silently=False,
        )
        count += 1

    return f"Correos enviados a {count} usuarios"