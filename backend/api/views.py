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
import secrets
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import PasswordResetOTP

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

            return Response({
                "message": "Password reset OTP sent to your email.",
                "email": email 
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "Email not registered."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to send email. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetOTPVerifyView(APIView):
    """
    Verify OTP and return a temporary reset token.
    """

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"error": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try getting OTP record tied to that user email
        otp_instance = PasswordResetOTP.objects.filter(
            user__email=email,
            otp=otp,
            used=False
        ).order_by('-expires_at').first()

        if not otp_instance:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if OTP expired
        if not otp_instance.is_valid():
            return Response(
                {"error": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used to prevent reuse
        otp_instance.used = True

        # Generate secure reset token (valid for 10 mins)
        reset_token = secrets.token_urlsafe(32)
        token_expiry = timezone.now() + timedelta(minutes=10)

        otp_instance.reset_token = reset_token
        otp_instance.reset_token_expires_at = token_expiry
        otp_instance.save()

        return Response(
            {
                "message": "OTP verified successfully.",
                "reset_token": reset_token,
                "expires_in_minutes": 10
            },
            status=status.HTTP_200_OK
        )


User = get_user_model()  # IMPORTANT


class PasswordResetCompleteView(APIView):
    """
    Final step: user enters new password.
    OTP already verified. Only reset_token + email required.
    """

    def post(self, request):
        email = request.data.get("email")
        reset_token = request.data.get("reset_token")
        new_password = request.data.get("password")

        if not email or not reset_token or not new_password:
            return Response({"error": "Email, reset token, and new password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP verification happened previously
        otp_instance = PasswordResetOTP.objects.filter(
            user__email=email,
            used=True  # This means OTP verification was successful
        ).order_by('-expires_at').first()

        if not otp_instance:
            return Response({"error": "OTP verification missing. Restart reset process."},
                            status=status.HTTP_400_BAD_REQUEST)

        # (Optional) Validate token format length for sanity (not DB check)
        if len(reset_token) < 10:
            return Response({"error": "Invalid token format."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Reset password
        user = otp_instance.user
        user.set_password(new_password)
        user.save()

        # Clean up reset process
        otp_instance.delete()  # removes OTP entirely so reset cannot repeat

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


