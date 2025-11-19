from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from .serializers import SignUpSerializer, SignInSerializer
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
import random
from .models import CustomUser, PasswordResetOTP
from django.conf import settings

# --- Signup view ---
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Login view ---
class SignInView(APIView):
    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "fullname": user.fullname,
                "email": user.email
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users

    def get(self, request):
        user = request.user  # User from JWT token

        # Return any details you want
        data = {
            "fullname": user.fullname,
            "email": user.email,
            "id": user.id,
        }

        return Response(data)

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)

            # --- Generate OTP ---
            otp = str(random.randint(100000, 999999))  # 6-digit OTP
            expiry_time = timezone.now() + timedelta(minutes=15)

            # Save OTP to database
            PasswordResetOTP.objects.create(user=user, otp=otp, expires_at=expiry_time)

            # --- Send email ---
            subject = "Your Password Reset OTP"
            message = f"Hello {user.fullname or user.email},\n\nYour OTP for password reset is: {otp}\nIt will expire in 15 minutes.\n\nIf you did not request this, please ignore this email."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({"message": "Password reset OTP sent to your email."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Email not registered."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to send email. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
