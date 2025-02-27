from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.urls import router, business_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(business_router.urls)),
    path('', include('core.urls')),  # Include all URLs from core.urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 