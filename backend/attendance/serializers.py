# attendance/serializers.py
from rest_framework import serializers
from .models import attendanceRecord
from .models import companyProfile

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = companyProfile
        fields = '__all__'
class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = attendanceRecord
        fields = '__all__'
        read_only_fields = ('user', 'companyProfile', 'created_at', 'check_in_time', 'check_out_time', 'photo')
