from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .utils import validate_and_format_phone

class Agency(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, through='AgencyUser', related_name='agencies')
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
        verbose_name_plural = "agencies"
        ordering = ['name']


class AgencyUser(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('agent', 'Agent'),
        ('staff', 'Staff'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'agency']
        verbose_name = 'Agency User'
        verbose_name_plural = 'Agency Users'
        indexes = [
            models.Index(fields=['user', 'agency']),
            models.Index(fields=['agency', 'role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.agency.name} ({self.role})"

    def save(self, *args, **kwargs):
        # Ensure only one primary user per agency
        if self.is_primary:
            AgencyUser.objects.filter(agency=self.agency, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs) 