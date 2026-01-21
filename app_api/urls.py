from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import index, UserViewSet
from tasks.views import TaskViewSet, TaskLogViewSet, dashboard_stats

# Router Principal
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'logs', TaskLogViewSet)
router.register(r'users', UserViewSet)

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
    
    path('health/', health_check),
    path('', index),
    path('api/stats/', dashboard_stats), # Nova rota de stats
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]

