from django.db import models
from django.contrib.auth.models import User
import os
from ..managers import DocumentManager, BusinessDocumentManager
from .base import TimeStampedModel

class Document(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    businesses = models.ManyToManyField('Business', related_name='documents', through='BusinessDocument')
    agency_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=False)

    objects = DocumentManager()

    class Meta(TimeStampedModel.Meta):
        indexes = [
            models.Index(fields=['agency_owner', 'is_public']),
            models.Index(fields=['name'])
        ]
        permissions = [
            ("can_make_public", "Can make document public"),
            ("can_make_private", "Can make document private"),
        ]

    def __str__(self):
        return self.name

    @property
    def is_template(self):
        """Returns whether this document is a template (has fields)."""
        return self.fields.exists()

class BusinessDocument(TimeStampedModel):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed')
    ]

    business = models.ForeignKey('Business', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    objects = BusinessDocumentManager()

    class Meta(TimeStampedModel.Meta):
        unique_together = ['business', 'document']
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['document', 'status'])
        ]

    def __str__(self):
        return f"{self.business.name} - {self.document.name}"

    @property
    def is_complete(self):
        """Returns whether this document is complete."""
        return self.status == self.COMPLETED

    def mark_as_complete(self):
        """Marks the document as complete."""
        self.status = self.COMPLETED
        self.save()

def uploaded_business_document_path(instance, filename):
    """Generate the upload path for business documents."""
    # File will be uploaded to MEDIA_ROOT/uploaded_documents/business_<id>/<filename>
    return f'uploaded_documents/business_{instance.business.id}/{filename}'

class UploadedBusinessDocument(TimeStampedModel):
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

    class Meta(TimeStampedModel.Meta):
        verbose_name = 'Uploaded Business Document'
        verbose_name_plural = 'Uploaded Business Documents'
        indexes = [
            models.Index(fields=['business', 'created_at'])
        ]

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        # Delete the file when the model instance is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    @property
    def file_size(self):
        """Returns the file size in bytes."""
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0

    @property
    def file_extension(self):
        """Returns the file extension."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return '' 