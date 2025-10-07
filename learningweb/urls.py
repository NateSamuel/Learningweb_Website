from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
def favicon(request):
    return HttpResponse(status=204)

urlpatterns = [
    path('', include('learningapp.urls')),
    path('admin/', admin.site.urls),
    path('favicon.ico', favicon),
    path('chat/', include('chat.urls')),
    path('apischema/',
        get_schema_view(title='LEARNINGWEB REST API',
        description="API for interacting with learning data",
        version="1.0"),
        name = "openapi-schema"),
    path('swaggerdocs/', TemplateView.as_view(
        template_name='learningapp/swagger-docs.html',
        extra_context={'schema_url':'openapi-schema'}),
        name='swagger-ui'),    
]