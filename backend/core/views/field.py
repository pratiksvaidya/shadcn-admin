from rest_framework import viewsets, permissions
from ..models import Field, FieldValue
from ..serializers import FieldSerializer, FieldValueSerializer
from rest_framework.response import Response
from rest_framework import status

class FieldViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated]

class FieldValueViewSet(viewsets.ModelViewSet):
    serializer_class = FieldValueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FieldValue.objects.filter(
            customer__agency_owner=self.request.user
        ) | FieldValue.objects.filter(
            business__customer__agency_owner=self.request.user
        )

    def create(self, request, *args, **kwargs):
        # Check if a field value already exists
        field_id = request.data.get('field')
        customer_id = request.data.get('customer')
        business_id = request.data.get('business')

        existing = FieldValue.objects.filter(
            field_id=field_id,
            customer_id=customer_id,
            business_id=business_id
        ).first()

        if existing:
            # Update existing value
            serializer = self.get_serializer(existing, data=request.data)
        else:
            # Create new value
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers) 