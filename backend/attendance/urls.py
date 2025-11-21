from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf.urls.static import static
from django.conf import settings
from .views import AttendanceCheckInView, AttendanceCheckOutView
# from .views import 

# Simple API check view
class APICheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "message": "API is running"})

urlpatterns = [
    path('checkin/', AttendanceCheckInView.as_view(), name='checkin'),
    path('checkout/', AttendanceCheckOutView.as_view(), name='checkin'),
    path('api-check/', APICheckView.as_view(), name='api_check'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
