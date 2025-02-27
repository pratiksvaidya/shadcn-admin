from rest_framework import serializers
from ..models import Field, FieldValue

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'

class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'business', 'value', 'source', 'source_id', 'created_at', 'updated_at'] 