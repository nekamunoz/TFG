from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sign-in/', views.signin, name='sign-in'),
    path('sign-up/', views.signup, name='sign-up'),
    path('profile/', views.profile, name='profile'),
]