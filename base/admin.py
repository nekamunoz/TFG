from django.contrib import admin
from .models import CustomUser, Appointment, Doctor, Patient

admin.site.register(CustomUser)
admin.site.register(Appointment)
admin.site.register(Doctor)
admin.site.register(Patient)
