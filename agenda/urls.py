from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.agenda, name='agenda'),
    path('appointment/', views.appointment, name='appointment'),
    path("create_appointment/", views.create_appointment, name="create_appointment"),
]