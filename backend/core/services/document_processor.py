import io
from typing import BinaryIO, Any, Union
# import PyPDF2
from ..models import Business, Document, Field, FieldValue, UploadedBusinessDocument
from django.core.files import File
from datetime import datetime

class DocumentProcessor:
    def __init__(self, file: BinaryIO):
        self.file = file

    def process(self) -> None:
        """
        Process the uploaded file and update business data if applicable.
        """
        try:
            if self.file.name.endswith('.pdf'):
                self._process_pdf()
            else:
                raise Exception("Unsupported file type. Only PDF files are supported.")
            
        except Exception as e:
            raise Exception(f"Failed to process file: {str(e)}")

    def _process_pdf(self) -> None:
        """
        Process PDF file content
        """
        pdf_reader = PyPDF2.PdfReader(self.file)
        # Add PDF processing logic here
        # This is where you would implement the business logic for PDF files

class UploadedDocumentProcessor:
    def __init__(self, file, business: Business, uploaded_doc: UploadedBusinessDocument):
        self.file = file
        self.business = business
        self.uploaded_doc = uploaded_doc

    def process(self):
        """Process the uploaded document and extract field values."""
        # Example field mappings from the document
        field_values = {
            'certificate_date': '07/22/2024',
            'name': 'The Laundry Genius Inc',
            'address': '7807 Evergreen Way, Everett, WA 98203-6427',
            'policy_number': 'BIP-4W906929-24-42',
            'carrier_name': 'Fidelity and Guaranty Insurance Company',
            'agency_name': 'Brooks Waterburn Corp',
            'agency_address': '1105 Broadhollow Rd',
            'agency_city': 'Farmingdale',
            'agency_state': 'NY',
            'agency_zip': '11735-4818',
            'proposed_effective_date': '09/01/2024',
            'policy_expiration_date': '09/01/2025',
            'billing_plan_direct': 'True',
            'policy_premium': '$3,932.00',
            'business_type': 'Corporation',
            'business_description': 'Laundromat Business'
        }

        # Store field values
        self._store_field_values(field_values, self.uploaded_doc)

    def _store_field_values(self, field_values: dict, uploaded_doc: UploadedBusinessDocument):
        """Store the extracted field values in the database."""
        field_mapping = {
            'certificate_date': 'date',
            'name': 'applicant_name',
            'address': 'premises_address',
            'policy_number': 'policy_number',
            'carrier_name': 'carrier_name',
            'agency_name': 'agency_name',
            'agency_address': 'agency_address',
            'agency_city': 'agency_city',
            'agency_state': 'agency_state',
            'agency_zip': 'agency_zip',
            'proposed_effective_date': 'proposed_effective_date',
            'policy_expiration_date': 'policy_expiration_date',
            'billing_plan_direct': 'billing_plan_direct',
            'policy_premium': 'policy_premium',
            'business_type': 'business_type',
            'business_description': 'business_description'
        }

        # Get all fields for efficiency
        fields = {
            field.field_id: field 
            for field in Field.objects.filter(field_id__in=field_mapping.values())
        }

        # Create or update field values
        for key, value in field_values.items():
            field_id = field_mapping.get(key)
            if field_id and field_id in fields:
                field = fields[field_id]
                if value is not None:
                    # Create or update field value
                    FieldValue.objects.update_or_create(
                        field=field,
                        business=self.business,
                        defaults={
                            'value': value,
                            'source': 'document',
                            'source_id': uploaded_doc.id
                        }
                    )

    def _update_business_data(self, data: dict) -> None:
        """
        Update business fields if they exist in the data
        """
        fields_to_update = {
            'name': data.get('name'),
            'address': data.get('address'),
            'phone_number': data.get('phone_number'),
            'email': data.get('email'),
            'description': data.get('description')
        }

        update_needed = False
        for field, value in fields_to_update.items():
            if value and not getattr(self.business, field):
                setattr(self.business, field, value)
                update_needed = True

        if update_needed:
            self.business.save()