import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
from core.models import BusinessDocument, FieldValue, validate_and_format_phone
from django.core.exceptions import ValidationError

# Load environment variables
load_dotenv()

class ContactCustomerService:
    VAPI_API_URL = "https://api.vapi.ai/call"
    VAPI_API_KEY = os.environ.get("VAPI_API_KEY")
    ASSISTANT_ID = "57e4e571-0070-482d-a01c-fb8d1792f1fe"
    PHONE_NUMBER_ID = "6c54d848-e6cb-4fd8-b726-738b6d6902d2"

    @staticmethod
    def _get_missing_required_fields(business_document: BusinessDocument) -> List[Dict]:
        """Get required fields that don't have values for this business."""
        # Get all required fields for this document
        required_fields = business_document.document.fields.filter(is_required=True)
        
        # Get existing field values
        existing_values = FieldValue.objects.filter(
            field__document=business_document.document,
            business=business_document.business
        ).values_list('field_id', flat=True)
        
        # Find missing required fields
        missing_fields = required_fields.exclude(id__in=existing_values)
        
        return [
            {
                "field_id": field.field_id,
                "name": field.name,
                "field_type": field.field_type,
                "description": field.description
            }
            for field in missing_fields
        ]

    @staticmethod
    def _get_schema_type_and_enum(field_id: str, field_type: str) -> tuple:
        """Get the schema type and enum values for a field."""
        if field_type == "number":
            return "number", None
        elif field_type == "boolean":
            return "boolean", None
        elif field_type == "date":
            return "string", None
            
        # Add enums for specific fields
        if field_id == "business_type":
            return "string", ["Corporation", "Individual", "Partnership"]
            
        return "string", None

    @staticmethod
    def call_customer(business_document: BusinessDocument) -> dict:
        """
        Initiates a call to the customer associated with the business document using Vapi.
        
        Args:
            business_document (BusinessDocument): The business document instance
            
        Returns:
            dict: A dictionary containing the status and message of the call
        """
        try:
            business_name = business_document.business.name
            customer_name = f"{business_document.business.customer.first_name} {business_document.business.customer.last_name}"
            customer_phone = business_document.business.customer.phone_number
            
            # Ensure phone number is in E.164 format
            try:
                customer_phone = validate_and_format_phone(customer_phone)
            except ValidationError as e:
                return {
                    'status': 'error',
                    'message': f'Invalid phone number: {str(e)}'
                }
            
            # Get missing required fields
            missing_fields = ContactCustomerService._get_missing_required_fields(business_document)
            missing_fields_text = "\n".join([
                f"- {field['name']} ({field['description']})" 
                for field in missing_fields
            ])
            
            # Build schema properties for each missing field
            schema_properties = {}
            for field in missing_fields:
                field_type, enum_values = ContactCustomerService._get_schema_type_and_enum(
                    field["field_id"], 
                    field["field_type"]
                )
                
                property_def = {
                    "type": field_type,
                    "description": field["description"]
                }
                
                if enum_values:
                    property_def["enum"] = enum_values
                
                schema_properties[field["field_id"]] = property_def
            
            # Prepare the request payload
            payload = {
                "assistantId": ContactCustomerService.ASSISTANT_ID,
                "phoneNumberId": ContactCustomerService.PHONE_NUMBER_ID,
                "customer": {
                    "name": customer_name,
                    "number": customer_phone
                },
                "assistantOverrides": {
                    "analysisPlan": {
                        "structuredDataPlan": {
                            "enabled": True,
                            "schema": {
                                "type": "object",
                                "properties": schema_properties,
                                "required": list(schema_properties.keys())
                            }
                        },
                    },
                    "variableValues": {
                        "businessName": business_name,
                        "customerName": customer_name,
                        "missingFields": missing_fields_text
                    }
                }
            }
            
            # Make the API call
            headers = {
                "Authorization": f"Bearer {ContactCustomerService.VAPI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                ContactCustomerService.VAPI_API_URL,
                json=payload,
                headers=headers
            )
            
            response_data = response.json()
            
            # Check if the call was queued successfully
            if response.status_code == 201 and response_data.get('status') == 'queued':
                return {
                    'status': 'success',
                    'message': f'Initiated call to {customer_name} for {business_name}',
                    'details': {
                        'customer_name': customer_name,
                        'customer_phone': customer_phone,
                        'business_name': business_name,
                        'call_id': response_data.get('id'),
                        'call_status': response_data.get('status'),
                        'missing_fields': missing_fields
                    }
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to initiate call: {response.text}'
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to initiate call: {str(e)}'
            } 