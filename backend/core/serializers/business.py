from rest_framework import serializers
from ..models import Business

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'description', 'address', 'phone_number', 'email', 'customer', 'created_at', 'updated_at']

class BusinessDetailSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = ['id', 'name', 'description', 'address', 'phone_number', 'email', 'customer', 'documents', 'created_at', 'updated_at']

    def get_documents(self, obj):
        from .document import BusinessDocumentSerializer
        documents = obj.businessdocument_set.all()
        return BusinessDocumentSerializer(documents, many=True).data 