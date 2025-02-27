from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from .models.utils import validate_and_format_phone
from .models.agency import Agency, AgencyUser

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='customers')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = validate_and_format_phone(self.phone_number)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        indexes = [
            models.Index(fields=['agency', 'created_at']),
            models.Index(fields=['email']),
        ]

class Business(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    customer = models.ForeignKey(Customer, related_name='businesses', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = validate_and_format_phone(self.phone_number)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "businesses"

class Document(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    businesses = models.ManyToManyField(Business, related_name='documents', through='BusinessDocument')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BusinessDocument(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['business', 'document']

class Field(models.Model):
    field_id = models.CharField(max_length=50, unique=True, help_text='Unique identifier for the field')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    document = models.ForeignKey(Document, related_name='fields', on_delete=models.CASCADE)
    is_required = models.BooleanField(default=False)
    field_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean')
    ], default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document.name} - {self.name}"

class FieldValue(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, related_name='field_values', on_delete=models.CASCADE)
    value = models.TextField()
    source = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('document', 'Document'),
            ('phone', 'Phone'),
            ('email', 'Email')
        ],
        default='manual'
    )
    source_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID reference to the source (document, phone, or email) if not manual'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['field', 'business']

    def __str__(self):
        return f"{self.field.name} - {self.value}"

def uploaded_business_document_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/uploaded_documents/business_<id>/<filename>
    return f'uploaded_documents/business_{instance.business.id}/{filename}'

class UploadedBusinessDocument(models.Model):
    business = models.ForeignKey(
        'Business',
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )
    name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Optional name for the document'
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text='Optional description of the document'
    )
    file = models.FileField(
        upload_to=uploaded_business_document_path,
        help_text='The uploaded document file'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Uploaded Business Document'
        verbose_name_plural = 'Uploaded Business Documents'

    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs) 