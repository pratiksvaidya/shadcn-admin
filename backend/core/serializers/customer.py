from rest_framework import serializers
from ..models import Customer
from .business import BusinessSerializer

class CustomerSerializer(serializers.ModelSerializer):
    businesses = BusinessSerializer(many=True, read_only=True)
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'businesses', 
            'agency',
            'agency_name',
            'created_by',
            'created_by_username',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['agency', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['agency_owner'] = self.context['request'].user
        return super().create(validated_data) 