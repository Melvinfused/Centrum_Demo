from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('attendance/', include('attendance.urls')),
    path('sitevisit/', include('sitevisit.urls')),

]

