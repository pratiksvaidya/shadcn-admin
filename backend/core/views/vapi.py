from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ..services.vapi_service import VapiService

@api_view(['POST'])
@permission_classes([AllowAny])
def vapi_webhook(request):
    """Handle webhook events from VAPI."""
    result = VapiService.process_webhook_event(request.data)
    return Response(
        {
            'status': result['status'],
            'message': result['message']
        },
        status=result['http_status']
    ) 