from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from .serializers import SignUpSerializer, SignInSerializer

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