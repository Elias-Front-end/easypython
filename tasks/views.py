from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Task, TaskLog
from .serializers import TaskSerializer, TaskLogSerializer
from .tasks import execute_task

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """
        Endpoint para disparar a tarefa manualmente via Celery.
        """
        task = self.get_object()
        # Dispara tarefa assíncrona
        execute_task.delay(task.id)
        return Response({'status': 'queued', 'message': 'Tarefa enviada para execução.'})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Retorna o histórico de execuções desta tarefa.
        """
        task = self.get_object()
        logs = TaskLog.objects.filter(task=task)[:50] # Aumentado para 50
        serializer = TaskLogSerializer(logs, many=True)
        return Response(serializer.data)

class TaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar logs globais com filtros.
    """
    queryset = TaskLog.objects.all().order_by('-created_at')
    serializer_class = TaskLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['task__title', 'status', 'output']
    ordering_fields = ['created_at', 'duration']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        task_id = self.request.query_params.get('task_id')
        
        if status:
            queryset = queryset.filter(status=status)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
            
        return queryset

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    Retorna estatísticas para o dashboard.
    """
    total_tasks = Task.objects.count()
    active_tasks = Task.objects.filter(enabled=True).count()
    
    # Logs das últimas 24h ou geral
    total_executions = TaskLog.objects.count()
    failed_executions = TaskLog.objects.filter(status='error').count()
    
    # Calcular taxa de sucesso
    success_rate = 0
    if total_executions > 0:
        success_count = TaskLog.objects.filter(status='success').count()
        success_rate = round((success_count / total_executions) * 100, 1)

    return Response({
        'total_tasks': total_tasks,
        'active_tasks': active_tasks,
        'total_executions': total_executions,
        'failed_executions': failed_executions,
        'success_rate': success_rate,
        # 'workers_online': 1 # Placeholder, difícil obter sem conexão direta com Celery Control
    })

