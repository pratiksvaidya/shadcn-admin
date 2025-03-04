# Generated by Django 5.1.3 on 2025-02-25 08:22

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_migrate_customers_to_agency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('policy_number', models.CharField(blank=True, help_text='The policy number assigned by the carrier', max_length=100, null=True)),
                ('effective_date', models.DateField(blank=True, help_text='The date the policy becomes effective', null=True)),
                ('expiration_date', models.DateField(blank=True, help_text='The date the policy expires', null=True)),
                ('carrier', models.CharField(blank=True, help_text='The insurance carrier providing the policy', max_length=200, null=True)),
                ('annual_premium', models.DecimalField(blank=True, decimal_places=2, help_text='The annual premium amount in dollars', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('policy_type', models.CharField(blank=True, choices=[('general_liability', 'General Liability'), ('commercial_property', 'Commercial Property'), ('workers_comp', 'Workers Compensation'), ('commercial_auto', 'Commercial Auto'), ('professional_liability', 'Professional Liability'), ('business_interruption', 'Business Interruption')], help_text='The type of insurance policy', max_length=50, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='policies', to='core.business')),
                ('documents', models.ManyToManyField(blank=True, help_text='Documents associated with this policy', related_name='policies', to='core.uploadedbusinessdocument')),
            ],
            options={
                'verbose_name': 'Policy',
                'verbose_name_plural': 'Policies',
                'ordering': ['-effective_date', 'policy_type'],
                'abstract': False,
                'indexes': [models.Index(fields=['business', 'policy_type'], name='core_policy_busines_2bccb9_idx'), models.Index(fields=['effective_date'], name='core_policy_effecti_3952fd_idx'), models.Index(fields=['expiration_date'], name='core_policy_expirat_076eb1_idx'), models.Index(fields=['carrier'], name='core_policy_carrier_5dba0c_idx')],
            },
        ),
    ]
