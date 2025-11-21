from rest_framework import serializers
from .models import sitevisitRecord
from .models import siteProfile

class siteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = siteProfile
        fields = '__all__'
class SiteVisitRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = sitevisitRecord
        fields = '__all__'
        read_only_fields = ('user', 'siteProfile', 'created_at', 'check_in_time', 'check_out_time', 'photo')

class SiteVisitHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = sitevisitRecord
        fields = ('check_in_time', 'check_out_time')
    
    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None