from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import sitevisitRecord, siteProfile
from .serializers import SiteVisitRecordSerializer
import math

# Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate distance in kilometers between two lat/lon points
    """
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class SiteVisitCheckInView(generics.CreateAPIView):
    serializer_class = SiteVisitRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        today = timezone.localdate()

        # Prevent double check-in in the same day (based on check_in_time datetime field)
        if sitevisitRecord.objects.filter(user=user, check_in_time__date=today).exists():
            return Response({"error": "You have already checked in today."}, status=status.HTTP_400_BAD_REQUEST)

        # Read input coordinates
        input_lat = request.data.get("latitude")
        input_lon = request.data.get("longitude")

        if not all([input_lat, input_lon]):
            return Response({"error": "Coordinates required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            input_lat = float(input_lat)
            input_lon = float(input_lon)
        except (TypeError, ValueError):
            return Response({"error": "Invalid coordinate format."}, status=status.HTTP_400_BAD_REQUEST)

        # --- Determine the user's assigned company ---
        assigned_site = None

        # Try common attribute names for the user's company relation
        # (adjust this to your actual User model field name if you know it)
#        if hasattr(user, "company"):  # e.g., user.company (FK)
#            assigned_site = getattr(user, "company")
#        elif hasattr(user, "companyProfile"):  # e.g., user.companyProfile
#            assigned_site = getattr(user, "companyProfile")
        if getattr(user, "site_id", None):  # direct FK id on user
            assigned_site = siteProfile.objects.filter(id=user.site_id).first()

        # If still not found, return useful error
        if not assigned_site:
            return Response({"error": "No Site-Visit assigned to this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure company has coordinates
        if assigned_site.latitude is None or assigned_site.longitude is None:
            return Response({"error": "Assigned site does not have coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        # Compute distance between provided coords and user's company coords
        distance_km = haversine(
            input_lat,
            input_lon,
            float(assigned_site.latitude),
            float(assigned_site.longitude)
        )

        # Threshold: 12 meters = 0.012 km
        if distance_km > 0.012:
            # helpful debug info (you may remove the distance in production)
            return Response({
                "error": "You are not at your assigned Site.",
                "distance_meters": round(distance_km * 1000, 2),
                "site": {
                    "id": assigned_site.id,
                    "name": assigned_site.site_name,
                    "latitude": assigned_site.latitude,
                    "longitude": assigned_site.longitude
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.FILES.get("photo"):
            return Response({"error": "Photo is required for check-in."}, status=status.HTTP_400_BAD_REQUEST)
        # Auto-fill address from user's company
        address_to_save = assigned_site.site_address
        
        # Create attendance record (serializer should have companyProfile/user/check_in_time as read_only)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=user,
            siteProfile=assigned_site,
            check_in_time=timezone.now(),
            address=address_to_save,
            latitude=input_lat,
            longitude=input_lon,
            photo=request.FILES.get("photo")
        )

        return Response({"success": f"Checked in successfully at {assigned_site.site_name}!"}, status=status.HTTP_201_CREATED)

class SiteVisitCheckOutView(generics.CreateAPIView):
    serializer_class = SiteVisitRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        today = timezone.localdate()

        # Prevent double check-out
        if sitevisitRecord.objects.filter(user=user, check_out_time__date=today).exists():
            return Response({"error": "You have already checked out today."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Find today's active check-in
        existing_record = sitevisitRecord.objects.filter(
            user=user,
            check_in_time__date=today,
            check_out_time__isnull=True
        ).first()

        if not existing_record:
            return Response({"error": "No check-in found for today. You must check in first."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update ONLY the existing record
        existing_record.check_out_time = timezone.now()
        existing_record.save()

        return Response({"success": "Checked out successfully!"}, status=status.HTTP_200_OK)

