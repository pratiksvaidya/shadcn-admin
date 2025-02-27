from rest_framework import serializers
from ..models import Policy, UploadedBusinessDocument
from .uploaded_document import UploadedBusinessDocumentSerializer

class PolicySerializer(serializers.ModelSerializer):
    documents = UploadedBusinessDocumentSerializer(many=True, read_only=True)
    policy_type_display = serializers.CharField(source='get_policy_type_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id',
            'business',
            'business_name',
            'policy_number',
            'effective_date',
            'expiration_date',
            'carrier',
            'annual_premium',
            'policy_type',
            'policy_type_display',
            'is_active',
            'documents',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Check that effective_date is before expiration_date if both are provided.
        """
        effective_date = data.get('effective_date')
        expiration_date = data.get('expiration_date')

        if effective_date and expiration_date and effective_date > expiration_date:
            raise serializers.ValidationError({
                'effective_date': 'Effective date must be before expiration date.'
            })

        return data 