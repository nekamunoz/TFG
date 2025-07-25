from django.urls import path
from .views import dashboard, videochat, save_conversation, appointment_notes
from .status import confirm_appointment, reject_appointment, cancel_appointment, change_priority

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('change-priority/<int:appointment_id>/', change_priority, name='change-priority'),
    path('confirm-appointment/<int:appointment_id>/', confirm_appointment, name='confirm-appointment'),
    path('reject-appointment/<int:appointment_id>/', reject_appointment, name='reject-appointment'),
    path('cancel-appointment/<int:appointment_id>/', cancel_appointment, name='cancel-appointment'),
    path('videochat/<int:appointment_id>/', videochat, name='video-chat'),
    path('videochat/<int:appointment_id>/save_conversation/', save_conversation, name='save-conversation'),
    path('appointment_notes/<int:appointment_id>/', appointment_notes, name='appointment_notes'),
]