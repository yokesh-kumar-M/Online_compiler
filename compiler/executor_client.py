"""Client for the Code Executor Microservice."""
import logging
import time
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('compiler')


class ExecutorClient:
    """HTTP client to communicate with the executor microservice."""

    def __init__(self):
        self.base_url = settings.EXECUTOR_SERVICE_URL
        self.api_key = settings.EXECUTOR_API_KEY
        self.timeout = settings.CODE_EXECUTION_TIMEOUT + 5  # Extra buffer

    def execute(self, code: str, language: str = 'python', stdin: str = '') -> dict:
        """
        Send code to executor microservice for execution.
        Falls back to local execution if executor is unavailable.
        """
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/execute",
                json={
                    'code': code,
                    'language': language,
                    'stdin': stdin,
                    'timeout': settings.CODE_EXECUTION_TIMEOUT,
                    'max_output_size': settings.MAX_OUTPUT_SIZE,
                },
                headers={
                    'X-API-Key': self.api_key,
                    'Content-Type': 'application/json',
                },
                timeout=self.timeout,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                result = response.json()
                result['execution_time_ms'] = elapsed_ms
                return result
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                return {
                    'success': False,
                    'output': '',
                    'error': error_data.get('detail', f'Executor returned status {response.status_code}'),
                    'execution_time_ms': elapsed_ms,
                }

        except requests.ConnectionError:
            logger.warning("Executor service unavailable, using local fallback")
            return self._local_execute(code, language)
        except requests.Timeout:
            return {
                'success': False,
                'output': '',
                'error': f'Execution timed out after {settings.CODE_EXECUTION_TIMEOUT} seconds',
                'execution_time_ms': self.timeout * 1000,
            }
        except Exception as e:
            logger.error(f"Executor client error: {e}")
            return {
                'success': False,
                'output': '',
                'error': f'Execution error: {str(e)}',
                'execution_time_ms': 0,
            }

    def _local_execute(self, code: str, language: str) -> dict:
        """Fallback local execution (Python only)."""
        import subprocess
        import sys
        import tempfile
        import os

        if language != 'python':
            return {
                'success': False,
                'output': '',
                'error': f'Local execution only supports Python. Executor service required for {language}.',
                'execution_time_ms': 0,
            }

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            start = time.time()
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True, text=True,
                timeout=settings.CODE_EXECUTION_TIMEOUT,
                cwd=tempfile.gettempdir(),
            )
            elapsed_ms = int((time.time() - start) * 1000)

            os.unlink(temp_file)

            if result.returncode == 0:
                output = result.stdout[:settings.MAX_OUTPUT_SIZE]
                return {'success': True, 'output': output, 'error': '', 'execution_time_ms': elapsed_ms}
            else:
                return {'success': False, 'output': '', 'error': result.stderr, 'execution_time_ms': elapsed_ms}

        except subprocess.TimeoutExpired:
            return {'success': False, 'output': '', 'error': 'Execution timed out', 'execution_time_ms': settings.CODE_EXECUTION_TIMEOUT * 1000}
        except Exception as e:
            return {'success': False, 'output': '', 'error': str(e), 'execution_time_ms': 0}

    def health_check(self) -> bool:
        """Check if executor service is healthy."""
        cache_key = 'executor_health'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            resp = requests.get(f"{self.base_url}/health", timeout=3)
            healthy = resp.status_code == 200
            cache.set(cache_key, healthy, timeout=30)
            return healthy
        except Exception:
            cache.set(cache_key, False, timeout=10)
            return False

    def get_supported_languages(self) -> list:
        """Get languages supported by executor."""
        cache_key = 'executor_languages'
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            resp = requests.get(f"{self.base_url}/languages", headers={'X-API-Key': self.api_key}, timeout=5)
            if resp.status_code == 200:
                langs = resp.json()
                cache.set(cache_key, langs, timeout=300)
                return langs
        except Exception:
            pass

        return [{'name': 'python', 'display_name': 'Python', 'version': '3.12'}]
