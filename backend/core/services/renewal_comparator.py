import os
import json
from typing import Dict, Any, List, Tuple
from django.conf import settings
from anthropic import Anthropic
import openai
from django.db.models import Q
from core.models import Business, Customer, Agency, AgencyUser
from django.contrib.auth.models import User
from .prompts import get_renewal_comparison_system_prompt, get_renewal_comparison_user_prompt
import PyPDF2
import re

class RenewalComparator:
    def __init__(self, policy, provider="anthropic"):
        """
        Initialize the RenewalComparator.
        
        Args:
            policy: The policy to compare
            provider: The AI provider to use ('anthropic' or 'openai')
        """
        self.policy = policy
        self.provider = provider.lower()
        
        # Validate provider
        if self.provider not in ["anthropic", "openai"]:
            raise ValueError("Provider must be either 'anthropic' or 'openai'")
        
    def _get_policy_context_details(self):
        # Extract policy details for context using Django ORM
        business = self.policy.business
        
        # Get customer information
        customer_name = ""
        agency_name = ""
        agent_name = ""
        
        try:
            # Business has a direct relationship to Customer
            if hasattr(business, 'customer') and business.customer:
                customer = business.customer
                customer_name = f"{customer.first_name} {customer.last_name}".strip()
                
                # Customer has a direct relationship to Agency
                if hasattr(customer, 'agency') and customer.agency:
                    agency = customer.agency
                    agency_name = agency.name
                    
                    # Get an agency user (agent) if one exists
                    agency_user = AgencyUser.objects.filter(agency=agency).select_related('user').first()
                    if agency_user and agency_user.user:
                        user = agency_user.user
                        agent_name = f"{user.first_name} {user.last_name}".strip()
        
        except Exception as e:
            print(f"Error retrieving relationship data: {str(e)}")
        
        # Create context details dictionary
        context_details = {
            "business_name": business.name,
            "client_name": customer_name,
            "insurance_agency_name": agency_name or "",
            "insurance_agent_name": agent_name or ""
        }

        return context_details

    def compare(self):
        # Get all uploaded documents associated with this policy
        uploaded_documents = self.policy.documents.all()
        
        # Check if we have any documents to compare
        if not uploaded_documents.exists():
            return {"error": "No documents available for comparison"}
        
        # Get context details for the policy
        context_details = self._get_policy_context_details()
        
        # Prepare document contents for analysis
        document_contents = []
        for doc in uploaded_documents:
            try:
                # Get file path
                file_path = doc.file.path
                
                # Check if file is a PDF
                if file_path.lower().endswith('.pdf'):
                    # Extract text from PDF
                    text = self._extract_text_from_pdf(file_path)
                else:
                    # For non-PDF files, try to read as text
                    with open(file_path, 'r', errors='replace') as f:
                        text = f.read()
                
                document_contents.append({
                    "name": doc.name,
                    "content": text
                })
            except Exception as e:
                print(f"Error reading document {doc.name}: {str(e)}")
        
        # Create prompt for AI using the utility function
        system_prompt = get_renewal_comparison_system_prompt(context_details)
        user_prompt = get_renewal_comparison_user_prompt(document_contents)
        
        # Call the appropriate AI provider
        try:
            if self.provider == "anthropic":
                comparison_result = self._call_anthropic(system_prompt, user_prompt)
            else:  # openai
                comparison_result = self._call_openai(system_prompt, user_prompt)
            
            # Parse the response to extract email and attachment
            parsed_result = self._parse_response(comparison_result)
            
            return parsed_result
            
        except Exception as e:
            print(f"Error in compare method: {str(e)}")
            return {"error": f"Failed to generate comparison: {str(e)}"}
    
    def _call_anthropic(self, system_prompt, user_prompt):
        """Call the Anthropic API and return the response text."""
        # Initialize Anthropic client
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=4000,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract the response content
        return response.content[0].text
    
    def _call_openai(self, system_prompt, user_prompt):
        """Call the OpenAI API and return the response text."""
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract the response content
        return response.choices[0].message.content
    
    def _extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return f"[Could not extract text from PDF: {str(e)}]"
    
    def _parse_response(self, response_text):
        """Parse the response from AI to extract email and attachment."""
        try:
            # First try to parse as JSON
            try:
                # Clean up the response text to make it valid JSON
                cleaned_text = response_text.strip()
                # If the response starts with a newline and "email", it might be a malformed JSON
                if cleaned_text.startswith('"email"') or cleaned_text.startswith('\n"email"'):
                    # Try to convert it to a proper JSON object
                    cleaned_text = '{' + cleaned_text + '}'
                
                data = json.loads(cleaned_text)
                return data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract email and attachment using regex
                email_match = re.search(r'email["\s:]+(.+?)(?=attachment["\s:]+|$)', response_text, re.DOTALL)
                attachment_match = re.search(r'attachment["\s:]+(.+?)$', response_text, re.DOTALL)
                
                email = email_match.group(1).strip() if email_match else ""
                attachment = attachment_match.group(1).strip() if attachment_match else ""
                
                # Clean up quotes if present
                if email.startswith('"') and email.endswith('"'):
                    email = email[1:-1]
                if attachment.startswith('"') and attachment.endswith('"'):
                    attachment = attachment[1:-1]
                
                return {
                    "email": email,
                    "attachment": attachment,
                }
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            # If all parsing attempts fail, return the raw response
            return {
                "comparison": response_text,
                "parsing_error": str(e)
            }
