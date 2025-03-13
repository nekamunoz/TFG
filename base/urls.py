from django.urls import path
from .views.base import signin, signup, signout, profile
from .views.dashboard import dashboard
from .views.agenda import agenda

urlpatterns = [
    path('', signin, name='sign-in'),
    path('dashboard/', dashboard, name='dashboard'),
    path('sign-up/', signup, name='sign-up'),
    path('sign-out/', signout, name='sign-out'),
    path('agenda/', agenda, name='agenda'),
    path('profile/', profile, name='profile'),
]