from django.urls import path

from .views import agenda, appointment, create_appointment, appointment_details

urlpatterns = [
    path('agenda/', agenda, name='agenda'),
    path('appointment/', appointment, name='appointment'),
    path("create_appointment/", create_appointment, name="create_appointment"),
    path("appointment/<int:appointment_id>/", appointment_details, name="appointment_details")
]