from django.db import models
from django.core.validators import MinValueValidator
from .base import TimeStampedModel

class Policy(TimeStampedModel):
    GENERAL_LIABILITY = 'general_liability'
    COMMERCIAL_PROPERTY = 'commercial_property'
    WORKERS_COMP = 'workers_comp'
    COMMERCIAL_AUTO = 'commercial_auto'
    PROFESSIONAL_LIABILITY = 'professional_liability'
    BUSINESS_INTERRUPTION = 'business_interruption'

    POLICY_TYPE_CHOICES = [
        (GENERAL_LIABILITY, 'General Liability'),
        (COMMERCIAL_PROPERTY, 'Commercial Property'),
        (WORKERS_COMP, 'Workers Compensation'),
        (COMMERCIAL_AUTO, 'Commercial Auto'),
        (PROFESSIONAL_LIABILITY, 'Professional Liability'),
        (BUSINESS_INTERRUPTION, 'Business Interruption'),
    ]

    business = models.ForeignKey(
        'Business',
        on_delete=models.CASCADE,
        related_name='policies'
    )
    policy_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='The policy number assigned by the carrier'
    )
    effective_date = models.DateField(
        blank=True,
        null=True,
        help_text='The date the policy becomes effective'
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        help_text='The date the policy expires'
    )
    carrier = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='The insurance carrier providing the policy'
    )
    annual_premium = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text='The annual premium amount in dollars'
    )
    policy_type = models.CharField(
        max_length=50,
        choices=POLICY_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text='The type of insurance policy'
    )
    documents = models.ManyToManyField(
        'UploadedBusinessDocument',
        related_name='policies',
        blank=True,
        help_text='Documents associated with this policy'
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'
        indexes = [
            models.Index(fields=['business', 'policy_type']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['expiration_date']),
            models.Index(fields=['carrier']),
        ]
        ordering = ['-effective_date', 'policy_type']

    def __str__(self):
        return f"{self.get_policy_type_display() or 'Policy'} - {self.business.name} ({self.policy_number or 'No number'})"

    @property
    def is_active(self):
        """Returns whether the policy is currently active based on dates."""
        from django.utils import timezone
        today = timezone.now().date()
        if not self.effective_date or not self.expiration_date:
            return False
        return self.effective_date <= today <= self.expiration_date 