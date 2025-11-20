from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from .views import SignUpView, SignInView, DashboardView, PasswordResetRequestView, PasswordResetOTPVerifyView, PasswordResetCompleteView

# Simple API check view
class APICheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "message": "API is running"})

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-check/', APICheckView.as_view(), name='api_check'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', PasswordResetOTPVerifyView.as_view(), name='password_reset_verification'),
    path('password-reset/reset/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ]