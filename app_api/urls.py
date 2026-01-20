from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import index  # Importar a view do frontend

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok", "message": "API running on EasyPanel!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('health/', health_check),  # Mover health check para rota específica
    path('', index),  # Servir a interface na raiz
    path('api/', include('tasks.urls')), # Tasks API
]
