# Celery configuration for Django project
import os
from celery import Celery
from celery.schedules import crontab
from datetime import datetime

print("-----------", datetime.now(), "-------------------")

# Cargar configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mypage.settings")

celery_app = Celery("mypage", broker='redis://localhost:6379/0')

celery_app.conf.beat_schedule = {
    "enviar-correos-diarios": {
        "task": "base.tasks.enviar_correo_diario",
        "schedule": crontab(hour=9, minute="00"),  # Todos los días a las 9:00 AM
    },
}

celery_app.autodiscover_tasks()