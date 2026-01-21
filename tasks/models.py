from django.db import models
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Task(models.Model):
    TASK_TYPES = [
        ('script', 'Script Python'),
        ('command', 'Comando Shell'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default='script')
    code = models.TextField(help_text="Código Python ou Comando Bash")
    
    # Agendamento
    enabled = models.BooleanField(default=True)
    schedule = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TaskLog(models.Model):
    STATUS_CHOICES = [
        ('running', 'Rodando'),
        ('success', 'Sucesso'),
        ('error', 'Erro'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)
    duration = models.FloatField(null=True, help_text="Duração em segundos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
