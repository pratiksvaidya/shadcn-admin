from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Customer, Business, Document, BusinessDocument
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates sample customer data for testing'

    def handle(self, *args, **options):
        # Create a test user if it doesn't exist
        username = 'testuser'
        email = 'agent@insuranceagency.com'
        password = 'testpass123'

        user, created = User.objects.get_or_create(
            username=username,
            email=email,
            defaults={'is_staff': True}
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {username}'))

        # Sample customer data
        customers_data = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@smithautorepair.com',
                'phone_number': '+14155552671',
                'businesses': [
                    {
                        'name': 'Smith Auto Repair',
                        'description': 'Full-service auto repair shop',
                        'address': '123 Main St, San Francisco, CA 94105',
                        'phone_number': '+14155552671',
                        'email': 'service@smithautorepair.com'
                    }
                ]
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah@sfflowershop.com',
                'phone_number': '+14155552672',
                'businesses': [
                    {
                        'name': 'The Flower Shop',
                        'description': 'Premium florist and event decoration',
                        'address': '456 Market St, San Francisco, CA 94105',
                        'phone_number': '+14155552672',
                        'email': 'orders@sfflowershop.com'
                    }
                ]
            },
            {
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'michael@brownconstructionsf.com',
                'phone_number': '+14155552673',
                'businesses': [
                    {
                        'name': 'Brown Construction Co',
                        'description': 'Commercial and residential construction',
                        'address': '789 Howard St, San Francisco, CA 94105',
                        'phone_number': '+14155552673',
                        'email': 'info@brownconstructionsf.com'
                    }
                ]
            },
            {
                'first_name': 'Emily',
                'last_name': 'Davis',
                'email': 'emily@healthybitessf.com',
                'phone_number': '+14155552674',
                'businesses': [
                    {
                        'name': 'Healthy Bites Cafe',
                        'description': 'Organic cafe and juice bar',
                        'address': '321 Mission St, San Francisco, CA 94105',
                        'phone_number': '+14155552674',
                        'email': 'orders@healthybitessf.com'
                    }
                ]
            },
            {
                'first_name': 'David',
                'last_name': 'Wilson',
                'email': 'david@techsolutionsinc.io',
                'phone_number': '+14155552675',
                'businesses': [
                    {
                        'name': 'Tech Solutions Inc',
                        'description': 'IT consulting and services',
                        'address': '555 California St, San Francisco, CA 94104',
                        'phone_number': '+14155552675',
                        'email': 'support@techsolutionsinc.io'
                    }
                ]
            },
            {
                'first_name': 'Lisa',
                'last_name': 'Anderson',
                'email': 'lisa@andersonlegal.com',
                'phone_number': '+14155552676',
                'businesses': [
                    {
                        'name': 'Anderson Law Firm',
                        'description': 'Business and corporate law',
                        'address': '100 Pine St, San Francisco, CA 94111',
                        'phone_number': '+14155552676',
                        'email': 'contact@andersonlegal.com'
                    }
                ]
            },
            {
                'first_name': 'Robert',
                'last_name': 'Taylor',
                'email': 'robert@taylormfg.net',
                'phone_number': '+14155552677',
                'businesses': [
                    {
                        'name': 'Taylor Manufacturing',
                        'description': 'Custom metal fabrication',
                        'address': '200 Folsom St, San Francisco, CA 94105',
                        'phone_number': '+14155552677',
                        'email': 'sales@taylormfg.net'
                    }
                ]
            },
            {
                'first_name': 'Jennifer',
                'last_name': 'Martinez',
                'email': 'jennifer@jmdesignsf.com',
                'phone_number': '+14155552678',
                'businesses': [
                    {
                        'name': 'JM Design Studio',
                        'description': 'Interior design and decoration',
                        'address': '150 3rd St, San Francisco, CA 94103',
                        'phone_number': '+14155552678',
                        'email': 'studio@jmdesignsf.com'
                    }
                ]
            },
            {
                'first_name': 'William',
                'last_name': 'Clark',
                'email': 'william@clarkproperties.com',
                'phone_number': '+14155552679',
                'businesses': [
                    {
                        'name': 'Clark Property Management',
                        'description': 'Commercial property management',
                        'address': '400 Montgomery St, San Francisco, CA 94104',
                        'phone_number': '+14155552679',
                        'email': 'leasing@clarkproperties.com'
                    }
                ]
            },
            {
                'first_name': 'Patricia',
                'last_name': 'Lee',
                'email': 'patricia@goldengatesf.com',
                'phone_number': '+14155552680',
                'businesses': [
                    {
                        'name': 'Golden Gate Restaurant',
                        'description': 'Fine dining restaurant',
                        'address': '600 Grant Ave, San Francisco, CA 94108',
                        'phone_number': '+14155552680',
                        'email': 'reservations@goldengatesf.com'
                    }
                ]
            }
        ]

        # Create customers and their businesses
        with transaction.atomic():
            for customer_data in customers_data:
                businesses = customer_data.pop('businesses')
                customer, created = Customer.objects.get_or_create(
                    email=customer_data['email'],
                    defaults={
                        **customer_data,
                        'agency_owner': user
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created customer: {customer.first_name} {customer.last_name}'))
                
                for business_data in businesses:
                    business, created = Business.objects.get_or_create(
                        customer=customer,
                        name=business_data['name'],
                        defaults=business_data
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created business: {business.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample data')) 