from celery import shared_task
import subprocess
import time
import sys
import io
import logging
from django.utils import timezone
from datetime import timedelta
from .models import Task, TaskLog

# Configuração de logger de fallback
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def cleanup_old_logs(self, days=30):
    """
    Remove logs de execução mais antigos que 'days'.
    
    Args:
        days (int): Número de dias de retenção (padrão: 30)
    
    Returns:
        dict: Contagem de logs deletados
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = TaskLog.objects.filter(created_at__lt=cutoff_date).delete()
    
    return {"deleted": deleted_count, "cutoff_date": str(cutoff_date)}

@shared_task(bind=True)
def execute_task(self, task_id):
    """
    Executa o código da tarefa (Python ou Shell) e salva o log.
    Inclui mecanismo de fallback para logging crítico.
    """
    try:
        task_obj = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f"CRITICAL: Task {task_id} not found during execution.")
        return f"Task {task_id} not found"

    # Cria log inicial
    try:
        log = TaskLog.objects.create(task=task_obj, status='running')
    except Exception as e:
        logger.error(f"CRITICAL: Failed to create TaskLog for Task {task_id}: {e}")
        # Fallback: Tenta continuar mesmo sem log no banco (não recomendado, mas evita crash total)
        log = None

    start_time = time.time()
    
    stdout = ""
    stderr = ""
    status = "success"

    try:
        if task_obj.task_type == 'script':
            # Executa código Python em ambiente isolado (básico)
            # AVISO: Em produção real, usar sandbox como Docker ou RestrictedPython
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            
            try:
                exec(task_obj.code, {'__builtins__': __builtins__}, {})
                stdout = redirected_output.getvalue()
            except Exception as e:
                stderr = str(e)
                status = "error"
            finally:
                sys.stdout = old_stdout

        elif task_obj.task_type == 'command':
            # Executa comando Shell
            process = subprocess.run(
                task_obj.code, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=60 # Limite de 1 min por padrão
            )
            stdout = process.stdout
            stderr = process.stderr
            if process.returncode != 0:
                status = "error"

    except Exception as e:
        stderr = f"System Error: {str(e)}"
        status = "error"
        logger.error(f"Task {task_id} Execution Failed: {e}")

    # Atualiza log final
    duration = time.time() - start_time
    
    if log:
        try:
            log.status = status
            log.output = stdout
            log.error = stderr
            log.duration = duration
            log.save()
        except Exception as e:
            logger.critical(f"FAILED TO SAVE TASK LOG for Task {task_id}. Status: {status}. Error: {e}")
    else:
        # Fallback se log não foi criado: Logar no sistema
        logger.info(f"Task {task_id} finished (NO DB LOG). Status: {status}. Duration: {duration}s")

    return f"Task {task_id} finished with {status}"
