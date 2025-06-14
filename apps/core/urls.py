from django.urls import path
from .views import signin, signup, signout, profile

urlpatterns = [
    path('sign-in/', signin, name='sign-in'),
    path('sign-up/', signup, name='sign-up'),
    path('sign-out/', signout, name='sign-out'),
    path('profile/', profile, name='profile'),
]