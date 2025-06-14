from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard', permanent=False)),
    path('', include('apps.core.urls')),
    path('', include('apps.appointment.urls')),
    path('', include('apps.dashboard.urls'))
]
