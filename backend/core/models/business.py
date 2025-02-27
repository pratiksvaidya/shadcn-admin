from django.db import models
from .customer import validate_and_format_phone
from ..managers import BusinessManager
from .base import TimeStampedModel

class Business(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    customer = models.ForeignKey('Customer', related_name='businesses', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    objects = BusinessManager()

    class Meta(TimeStampedModel.Meta):
        verbose_name_plural = "businesses"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['name']),
            models.Index(fields=['email'])
        ]
        permissions = [
            ("view_business_documents", "Can view business documents"),
            ("upload_business_documents", "Can upload business documents"),
        ]

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = validate_and_format_phone(self.phone_number)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Returns the full address if available."""
        return self.address if self.address else "No address provided"

    @property
    def contact_info(self):
        """Returns a dictionary of contact information."""
        return {
            'phone': self.phone_number if self.phone_number else None,
            'email': self.email if self.email else None,
            'address': self.full_address
        } 