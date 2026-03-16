"""Celery tasks for async code execution and maintenance."""
import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('compiler')


@shared_task(bind=True, max_retries=2, default_retry_delay=5)
def execute_code_async(self, execution_id: str, code: str, language: str = 'python', stdin: str = ''):
    """Execute code asynchronously via Celery."""
    from snippets.models import ExecutionHistory
    from .executor_client import ExecutorClient

    try:
        execution = ExecutionHistory.objects.get(id=execution_id)
        execution.status = 'running'
        execution.save(update_fields=['status'])

        client = ExecutorClient()
        result = client.execute(code, language, stdin)

        execution.status = 'success' if result['success'] else 'error'
        execution.output = result.get('output', '')
        execution.error_output = result.get('error', '')
        execution.execution_time_ms = result.get('execution_time_ms', 0)
        execution.save()

        # Update user stats
        if execution.user:
            from django.db.models import F
            from accounts.models import User
            User.objects.filter(pk=execution.user_id).update(
                total_executions=F('total_executions') + 1,
                executions_today=F('executions_today') + 1,
                last_execution_at=timezone.now(),
            )

        return {
            'execution_id': str(execution_id),
            'status': execution.status,
            'output': execution.output[:500],
        }

    except ExecutionHistory.DoesNotExist:
        logger.error(f"Execution {execution_id} not found")
    except Exception as exc:
        logger.error(f"Async execution error: {exc}")
        raise self.retry(exc=exc)


@shared_task
def reset_daily_execution_counts():
    """Reset daily execution counters (run via Celery Beat at midnight)."""
    from accounts.models import User
    count = User.objects.filter(executions_today__gt=0).update(executions_today=0)
    logger.info(f"Reset daily execution counts for {count} users")


@shared_task
def update_system_metrics():
    """Aggregate system metrics (run hourly via Celery Beat)."""
    from .models import SystemMetrics
    from snippets.models import ExecutionHistory
    from accounts.models import User

    today = timezone.now().date()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    executions_today = ExecutionHistory.objects.filter(created_at__gte=today_start)

    metrics, _ = SystemMetrics.objects.get_or_create(date=today)
    metrics.total_executions = executions_today.count()
    metrics.successful_executions = executions_today.filter(status='success').count()
    metrics.failed_executions = executions_today.filter(status__in=['error', 'timeout']).count()
    metrics.active_users_today = User.objects.filter(last_execution_at__gte=today_start).count()

    avg_time = executions_today.filter(execution_time_ms__isnull=False).values_list('execution_time_ms', flat=True)
    if avg_time:
        metrics.average_execution_time_ms = sum(avg_time) / len(avg_time)

    metrics.save()
    logger.info(f"Updated system metrics for {today}")


@shared_task
def cleanup_old_executions(days=30):
    """Remove execution history older than N days."""
    from snippets.models import ExecutionHistory
    cutoff = timezone.now() - timedelta(days=days)
    count, _ = ExecutionHistory.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {count} old execution records")
