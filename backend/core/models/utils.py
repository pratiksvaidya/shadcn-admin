from django.core.exceptions import ValidationError
import re

def validate_and_format_phone(phone_number: str) -> str:
    """
    Validates and formats phone numbers to E.164 format.
    If no country code is provided, assumes US (+1).
    Raises ValidationError if the phone number is invalid.
    """
    # Remove any non-digit characters except leading +
    has_plus = phone_number.startswith('+')
    digits_only = re.sub(r'\D', '', phone_number)
    
    # Handle empty/invalid numbers
    if not digits_only:
        raise ValidationError('Phone number is required')
    
    # For US/Canada numbers (10 digits)
    if len(digits_only) == 10:
        return f'+1{digits_only}'
    
    # For US/Canada numbers with country code (11 digits starting with 1)
    if len(digits_only) == 11 and digits_only.startswith('1'):
        return f'+{digits_only}'
        
    # If number starts with '+' but doesn't have country code, assume US
    if has_plus and len(digits_only) == 9:  # Missing country code
        return f'+1{digits_only}'
    
    # If number starts with '00', convert to +
    if phone_number.startswith('00'):
        return f'+{digits_only}'
    
    # If it's a valid international number (has + and at least 11 digits)
    if has_plus and len(digits_only) >= 11:
        return f'+{digits_only}'
        
    # If it looks like a US number without + (starts with area code)
    if len(digits_only) == 9 and digits_only[0] in '2345':  # US area codes start with 2-5
        return f'+1{digits_only}'
    
    raise ValidationError('Invalid phone number format. Please include country code or use 10-digit US number.') 