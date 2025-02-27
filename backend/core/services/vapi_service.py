from typing import Dict, Any, Union
from django.core.exceptions import ValidationError
from datetime import datetime
from ..models import Customer, Business, Field, FieldValue

class VapiService:
    @staticmethod
    def process_webhook_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook events from VAPI.
        
        Args:
            event_data (Dict[str, Any]): The webhook event data from VAPI
            
        Returns:
            Dict[str, Any]: A dictionary containing the status and message of the processing
        """
        try:
            message = event_data.get('message', {})
            message_type = message.get('type')

            if message_type == 'end-of-call-report':
                return VapiService._process_end_of_call_report(message)

            return {
                'status': 'success',
                'message': 'Event processed',
                'http_status': 200
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error processing webhook: {str(e)}',
                'http_status': 500
            }

    @staticmethod
    def _process_end_of_call_report(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process end-of-call report from VAPI.
        
        Args:
            message (Dict[str, Any]): The message containing the end-of-call report
            
        Returns:
            Dict[str, Any]: A dictionary containing the status and message of the processing
        """
        # Get call details
        call = message.get('call', {})
        customer_info = call.get('customer', {})
        customer_phone = customer_info.get('number')

        # Find customer by phone number
        try:
            customer = Customer.objects.get(phone_number=customer_phone)
        except Customer.DoesNotExist:
            return {
                'status': 'error',
                'message': 'Customer not found',
                'http_status': 404
            }

        # Get structured data from analysis
        structured_data = message.get('analysis', {}).get('structuredData', {})

        if not structured_data:
            return {
                'status': 'success',
                'message': 'No structured data found',
                'http_status': 200
            }

        # Update field values for the customer's businesses
        VapiService._update_field_values(customer, structured_data, call.get('id'))

        return {
            'status': 'success',
            'message': 'Field values updated successfully',
            'http_status': 200
        }

    @staticmethod
    def _update_field_values(customer: Customer, structured_data: Dict[str, Any], call_id: str) -> None:
        """
        Update field values for all businesses of a customer based on structured data.
        
        Args:
            customer (Customer): The customer whose businesses need updating
            structured_data (Dict[str, Any]): The structured data containing field values
            call_id (str): The ID of the call for source tracking
        """
        businesses = Business.objects.filter(customer=customer)
        for business in businesses:
            for field_id, value in structured_data.items():
                try:
                    field = Field.objects.get(field_id=field_id)
                    if value is not None:
                        FieldValue.objects.update_or_create(
                            field=field,
                            business=business,
                            defaults={
                                'value': value,
                                'source': 'phone',
                            }
                        )
                except Field.DoesNotExist:
                    continue 