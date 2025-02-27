from rest_framework import serializers
from ..models import UploadedBusinessDocument
from .field import FieldValueSerializer

class UploadedBusinessDocumentSerializer(serializers.ModelSerializer):
    field_values = serializers.SerializerMethodField()

    class Meta:
        model = UploadedBusinessDocument
        fields = ['id', 'name', 'description', 'file', 'field_values', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_field_values(self, obj):
        field_values = obj.business.field_values.filter(
            source='document',
            source_id=obj.id
        )
        return FieldValueSerializer(field_values, many=True).data 