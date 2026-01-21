from rest_framework import serializers
from .models import Task, TaskLog
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

class TaskLogSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = TaskLog
        fields = ['id', 'task', 'task_title', 'status', 'output', 'error', 'duration', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    last_run = serializers.SerializerMethodField()
    cron_expression = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="Formato Cron: * * * * *")
    schedule_display = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'task_type', 'code', 'enabled', 'created_by', 'created_at', 'last_run', 'cron_expression', 'schedule_display']
        read_only_fields = ['created_by', 'created_at']

    def get_last_run(self, obj):
        last_log = obj.tasklog_set.first()
        if last_log:
            return {
                'status': last_log.status,
                'date': last_log.created_at,
                'duration': last_log.duration
            }
        return None
    
    def get_schedule_display(self, obj):
        if obj.schedule and obj.schedule.crontab:
            c = obj.schedule.crontab
            return f"{c.minute} {c.hour} {c.day_of_month} {c.month_of_year} {c.day_of_week}"
        return None

    def create(self, validated_data):
        cron_expr = validated_data.pop('cron_expression', None)
        user = self.context['request'].user
        validated_data['created_by'] = user
        task = super().create(validated_data)
        
        if cron_expr:
            self._update_schedule(task, cron_expr)
        
        return task

    def update(self, instance, validated_data):
        cron_expr = validated_data.pop('cron_expression', None)
        task = super().update(instance, validated_data)
        
        if cron_expr is not None:
            self._update_schedule(task, cron_expr)
            
        return task

    def _update_schedule(self, task, cron_expr):
        # Se cron_expr vazio, remove agendamento
        if not cron_expr.strip():
            if task.schedule:
                task.schedule.delete()
                task.schedule = None
                task.save()
            return

        parts = cron_expr.split()
        if len(parts) != 5:
            raise serializers.ValidationError({"cron_expression": "Formato inválido. Use: * * * * *"})

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month_of_year=parts[3],
            day_of_week=parts[4]
        )

        if task.schedule:
            task.schedule.crontab = schedule
            task.schedule.enabled = task.enabled
            task.schedule.save()
        else:
            pt = PeriodicTask.objects.create(
                crontab=schedule,
                name=f"task_{task.id}_{task.title}",
                task='tasks.tasks.execute_task',
                args=json.dumps([task.id]),
                enabled=task.enabled
            )
            task.schedule = pt
            task.save()

