from django.db import models
from django.core.exceptions import ValidationError
from .base import TimeStampedModel

class Field(TimeStampedModel):
    TEXT = 'text'
    NUMBER = 'number'
    DATE = 'date'
    BOOLEAN = 'boolean'

    FIELD_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (NUMBER, 'Number'),
        (DATE, 'Date'),
        (BOOLEAN, 'Boolean')
    ]

    field_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique identifier for the field'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    document = models.ForeignKey(
        'Document',
        related_name='fields',
        on_delete=models.CASCADE
    )
    is_required = models.BooleanField(default=False)
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        default=TEXT
    )

    class Meta(TimeStampedModel.Meta):
        ordering = ['name']
        indexes = [
            models.Index(fields=['document', 'field_id']),
            models.Index(fields=['field_type'])
        ]

    def __str__(self):
        return f"{self.document.name} - {self.name}"

    def clean(self):
        super().clean()
        # Ensure field_id is lowercase and contains no spaces
        if self.field_id:
            self.field_id = self.field_id.lower().replace(' ', '_')

class FieldValue(TimeStampedModel):
    MANUAL = 'manual'
    DOCUMENT = 'document'
    PHONE = 'phone'
    EMAIL = 'email'

    SOURCE_CHOICES = [
        (MANUAL, 'Manual'),
        (DOCUMENT, 'Document'),
        (PHONE, 'Phone'),
        (EMAIL, 'Email')
    ]

    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    business = models.ForeignKey(
        'Business',
        related_name='field_values',
        on_delete=models.CASCADE
    )
    value = models.TextField()
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=MANUAL
    )
    source_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID reference to the source (document, phone, or email) if not manual'
    )

    class Meta(TimeStampedModel.Meta):
        unique_together = ['field', 'business']
        indexes = [
            models.Index(fields=['business', 'source']),
            models.Index(fields=['field', 'source'])
        ]

    def __str__(self):
        return f"{self.field.name} - {self.value}"

    def clean(self):
        super().clean()
        self.validate_value_format()

    def validate_value_format(self):
        """Validates that the value matches the field type format."""
        if not self.value:
            if self.field.is_required:
                raise ValidationError(f"{self.field.name} is required")
            return

        if self.field.field_type == Field.NUMBER:
            try:
                float(self.value)
            except ValueError:
                raise ValidationError(f"{self.field.name} must be a number")

        elif self.field.field_type == Field.BOOLEAN:
            if self.value.lower() not in ['true', 'false', '1', '0']:
                raise ValidationError(f"{self.field.name} must be a boolean value")

        elif self.field.field_type == Field.DATE:
            from datetime import datetime
            try:
                datetime.strptime(self.value, '%Y-%m-%d')
            except ValueError:
                raise ValidationError(f"{self.field.name} must be in YYYY-MM-DD format") 