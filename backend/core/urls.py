from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    CustomerViewSet, BusinessViewSet, DocumentViewSet,
    FieldViewSet, FieldValueViewSet,
    get_csrf, login, logout, get_user,
    BusinessDocumentViewSet, UploadedBusinessDocumentViewSet,
    vapi_webhook, PolicyViewSet
)
from .views.agency import AgencyViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'fields', FieldViewSet, basename='field')
router.register(r'field-values', FieldValueViewSet, basename='field-value')
router.register(r'business-documents', BusinessDocumentViewSet, basename='business-document')
router.register(r'agencies', AgencyViewSet, basename='agency')
router.register(r'policies', PolicyViewSet, basename='policy')

# Create a nested router for uploaded documents under businesses
business_router = routers.NestedSimpleRouter(router, r'businesses', lookup='business')
business_router.register(r'uploaded-documents', UploadedBusinessDocumentViewSet, basename='business-uploaded-document')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(business_router.urls)),
    path('api/csrf/', get_csrf, name='csrf'),
    path('api/auth/login/', login, name='login'),
    path('api/auth/logout/', logout, name='logout'),
    path('api/auth/user/', get_user, name='user'),
    path('api/vapi/webhook/', vapi_webhook, name='vapi-webhook'),
] 