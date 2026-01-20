from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from .serializers import UserSerializer

def index(request):
    """Renderiza a página principal com a aplicação de tarefas."""
    return render(request, 'index.html')

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite ver usuários.
    (Read-Only para segurança neste exemplo)
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # Permite que qualquer um veja a lista de usuarios (apenas para demo)
    permission_classes = [permissions.AllowAny] 
