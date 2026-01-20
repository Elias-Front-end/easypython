from django.contrib import admin
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok", "message": "API running on EasyPanel!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),  # Root URL check
]
