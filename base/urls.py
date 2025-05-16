from django.urls import path
from .views.base import signin, signup, signout, profile
from .views.dashboard import dashboard, videochat
from .views.status import confirm_appointment, reject_appointment, cancel_appointment, change_priority

urlpatterns = [
    path('', signin, name='sign-in'),
    path('dashboard/', dashboard, name='dashboard'),
    path('sign-up/', signup, name='sign-up'),
    path('sign-out/', signout, name='sign-out'),
    path('profile/', profile, name='profile'),
    path('change-priority/<int:appointment_id>/', change_priority, name='change-priority'),
    path('confirm-appointment/<int:appointment_id>/', confirm_appointment, name='confirm-appointment'),
    path('reject-appointment/<int:appointment_id>/', reject_appointment, name='reject-appointment'),
    path('cancel-appointment/<int:appointment_id>/', cancel_appointment, name='cancel-appointment'),
    path('videochat/<int:appointment_id>/', videochat, name='video-chat'),
]