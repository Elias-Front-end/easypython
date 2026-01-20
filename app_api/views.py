from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, filters
from .serializers import UserSerializer

def index(request):
    """Renderiza a página principal com a aplicação de tarefas."""
    return render(request, 'index.html')

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite CRUD completo de usuários.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    
    # Filtros e Busca
    filterset_fields = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'username']

    def get_permissions(self):
        """
        Permite criação (POST) sem auth para registro.
        Outras ações exigem autenticação.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
