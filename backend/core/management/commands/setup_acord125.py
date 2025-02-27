from django.core.management.base import BaseCommand
from core.models import Document, Field

class Command(BaseCommand):
    help = 'Sets up the ACORD 125 document and its fields'

    def handle(self, *args, **options):
        # Create ACORD 125 document
        document, created = Document.objects.get_or_create(
            name='ACORD 125 - Commercial Insurance Application',
            defaults={
                'description': 'Commercial Insurance Application - Applicant Information Section'
            }
        )

        # Define fields based on the documentation
        fields_data = [
            # Basic Information
            {
                'field_id': 'date',
                'name': 'Date',
                'description': 'Certificate date',
                'field_type': 'date',
                'is_required': True
            },
            {
                'field_id': 'proposed_effective_date',
                'name': 'Proposed Effective Date',
                'description': 'Proposed effective date of the policy',
                'field_type': 'date',
                'is_required': True
            },
            # Agency Information
            {
                'field_id': 'agency_name',
                'name': 'Agency Name',
                'description': 'Agency name',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'agency_address',
                'name': 'Agency Address',
                'description': 'Agency address',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'agency_city',
                'name': 'Agency City',
                'description': 'Agency city',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'agency_state',
                'name': 'Agency State',
                'description': 'Agency state',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'agency_zip',
                'name': 'Agency Zip',
                'description': 'Agency zip code',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'agency_contact_name',
                'name': 'Agency Contact Name',
                'description': 'Agency contact name',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'agency_phone',
                'name': 'Agency Phone',
                'description': 'Agency phone number',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'agency_fax',
                'name': 'Agency Fax',
                'description': 'Agency fax number',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'agency_email',
                'name': 'Agency Email',
                'description': 'Agency email address',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'agency_code',
                'name': 'Agency Code',
                'description': 'Agency code',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'agency_customer_id',
                'name': 'Agency Customer ID',
                'description': 'Agency customer ID',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'agency_sub_code',
                'name': 'Agency Sub Code',
                'description': 'Agency sub code',
                'field_type': 'text',
                'is_required': False
            },
            # Carrier Information
            {
                'field_id': 'carrier_name',
                'name': 'Carrier Name',
                'description': 'Insurance carrier name',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'naic_code',
                'name': 'NAIC Code',
                'description': 'Carrier NAIC code',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'policy_number',
                'name': 'Policy Number',
                'description': 'Policy number',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'underwriter_office',
                'name': 'Underwriter Office',
                'description': 'Underwriter office address',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'company_policy',
                'name': 'Company Policy',
                'description': 'Company policy details',
                'field_type': 'text',
                'is_required': False
            },
            # Policy Information
            {
                'field_id': 'billing_plan_direct',
                'name': 'Billing Plan Direct',
                'description': 'Whether billing is direct',
                'field_type': 'boolean',
                'is_required': True
            },
            {
                'field_id': 'policy_premium',
                'name': 'Policy Premium',
                'description': 'Policy premium amount',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'minimum_premium',
                'name': 'Minimum Premium',
                'description': 'Minimum premium amount',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'deposit',
                'name': 'Deposit',
                'description': 'Deposit amount',
                'field_type': 'text',
                'is_required': False
            },
            # Premises Information
            {
                'field_id': 'loc_number',
                'name': 'LOC Number',
                'description': 'Location number',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'occupied_area',
                'name': 'Occupied Area',
                'description': 'Occupied area details',
                'field_type': 'text',
                'is_required': False
            },
            # Sections Attached
            {
                'field_id': 'commercial_property',
                'name': 'Commercial Property',
                'description': 'Is commercial property coverage needed?',
                'field_type': 'boolean',
                'is_required': True
            },
            {
                'field_id': 'business_personal_property',
                'name': 'Business Personal Property',
                'description': 'Business personal property value',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'business_income',
                'name': 'Business Income',
                'description': 'Is business income coverage needed?',
                'field_type': 'boolean',
                'is_required': True
            },
            {
                'field_id': 'crime',
                'name': 'Crime',
                'description': 'Is crime coverage needed?',
                'field_type': 'boolean',
                'is_required': True
            },
            {
                'field_id': 'electronic_data_proc',
                'name': 'Electronic Data Proc',
                'description': 'Is electronic data processing coverage needed?',
                'field_type': 'boolean',
                'is_required': False
            },
            # Attachments
            {
                'field_id': 'additional_premises',
                'name': 'Additional Premises',
                'description': 'Additional premises indicator',
                'field_type': 'boolean',
                'is_required': False
            },
            {
                'field_id': 'statement_schedule_values',
                'name': 'Statement / Schedule of Values',
                'description': 'Statement or schedule of values indicator',
                'field_type': 'boolean',
                'is_required': False
            },
            # Applicant Information
            {
                'field_id': 'applicant_name',
                'name': 'Applicant Name',
                'description': 'Full legal name of applicant',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'dba',
                'name': 'DBA',
                'description': 'Doing Business As name',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'mailing_address',
                'name': 'Mailing Address',
                'description': 'Primary mailing address',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'premises_address',
                'name': 'Premises Address',
                'description': 'Physical location of business',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'website_address',
                'name': 'Website Address',
                'description': 'Business website URL',
                'field_type': 'text',
                'is_required': False
            },
            # Business Information
            {
                'field_id': 'business_type',
                'name': 'Business Type',
                'description': 'Type of business (Corporation, Individual, Partnership, etc.)',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'sic_code',
                'name': 'SIC Code',
                'description': 'Standard Industrial Classification code',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'business_description',
                'name': 'Business Description',
                'description': 'Detailed description of business operations',
                'field_type': 'text',
                'is_required': True
            },
            {
                'field_id': 'years_in_business',
                'name': 'Years in Business',
                'description': 'Number of years the business has been operating',
                'field_type': 'number',
                'is_required': True
            },
            {
                'field_id': 'number_of_employees',
                'name': 'Number of Employees',
                'description': 'Total number of employees',
                'field_type': 'number',
                'is_required': True
            },
            {
                'field_id': 'annual_revenue',
                'name': 'Annual Revenue',
                'description': 'Annual gross revenue',
                'field_type': 'number',
                'is_required': True
            },
            # Contact Information
            {
                'field_id': 'contact_name',
                'name': 'Contact Name',
                'description': 'Primary contact person name',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'contact_title',
                'name': 'Contact Title',
                'description': 'Title/Position of contact person',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'contact_phone',
                'name': 'Contact Phone',
                'description': 'Phone number of contact person',
                'field_type': 'text',
                'is_required': False
            },
            {
                'field_id': 'contact_email',
                'name': 'Contact Email',
                'description': 'Email address of contact person',
                'field_type': 'text',
                'is_required': False
            }
        ]

        # Create fields
        for field_data in fields_data:
            Field.objects.get_or_create(
                document=document,
                field_id=field_data['field_id'],
                defaults={
                    'name': field_data['name'],
                    'description': field_data['description'],
                    'field_type': field_data['field_type'],
                    'is_required': field_data['is_required']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully set up ACORD 125 document and fields')) 