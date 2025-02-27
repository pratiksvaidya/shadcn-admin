from rest_framework import serializers
from ..models import Agency, AgencyUser

class AgencySerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = [
            'id',
            'name',
            'description',
            'email',
            'phone_number',
            'website',
            'is_active',
            'role',
            'is_primary',
            'created_at',
            'updated_at'
        ]

    def get_role(self, obj):
        request = self.context.get('request')
        if request and request.user:
            agency_user = AgencyUser.objects.filter(
                user=request.user,
                agency=obj
            ).first()
            return agency_user.role if agency_user else None
        return None

    def get_is_primary(self, obj):
        request = self.context.get('request')
        if request and request.user:
            agency_user = AgencyUser.objects.filter(
                user=request.user,
                agency=obj
            ).first()
            return agency_user.is_primary if agency_user else False
        return False 