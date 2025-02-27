from django.db import models
from django.db.models import Q

class CustomerManager(models.Manager):
    def for_user(self, user):
        """Get all customers for a specific user's agency."""
        return self.filter(agency__users=user)

class BusinessManager(models.Manager):
    def for_user(self, user):
        """Get all businesses for a specific user's agency."""
        return self.filter(customer__agency__users=user)

    def with_documents(self):
        """Get businesses with prefetched documents and field values."""
        return self.prefetch_related(
            'documents',
            'field_values',
            'field_values__field'
        )

class DocumentManager(models.Manager):
    def for_user(self, user):
        """Get all documents accessible by a user."""
        return self.filter(
            Q(agency_owner=user) |
            Q(is_public=True)
        )

    def with_fields(self):
        """Get documents with prefetched fields."""
        return self.prefetch_related('fields')

class BusinessDocumentManager(models.Manager):
    def for_business(self, business):
        """Get all documents for a specific business."""
        return self.filter(business=business).select_related(
            'document'
        ).prefetch_related(
            'document__fields',
            'business__field_values'
        )

    def for_user(self, user):
        """Get all business documents for a specific agency owner."""
        return self.filter(
            business__customer__agency_owner=user
        ).select_related('business', 'document') 