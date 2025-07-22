
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion_gaz.urls')),
    path('comptes/', include('django.contrib.auth.urls')),  
]