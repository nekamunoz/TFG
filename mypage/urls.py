from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('chat/', include('chat.urls')),
    path('agenda/', include('agenda.urls'))
]
