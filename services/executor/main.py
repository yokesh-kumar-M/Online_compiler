"""
Code Executor Microservice
FastAPI-based isolated code execution service.
"""
import os
import sys
import time
import uuid
import logging
import tempfile
import subprocess
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configuration
API_KEY = os.environ.get('EXECUTOR_API_KEY', 'dev-executor-api-key')
DEFAULT_TIMEOUT = int(os.environ.get('CODE_EXECUTION_TIMEOUT', 10))
MAX_OUTPUT_SIZE = int(os.environ.get('MAX_OUTPUT_SIZE', 10000))
MAX_CODE_SIZE = 50000  # 50KB
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger('executor')

# Supported languages configuration
LANGUAGES = {
    'python': {
        'display_name': 'Python',
        'version': '3.12',
        'command': [sys.executable],
        'file_extension': '.py',
        'template': '# Python code here\nprint("Hello, World!")\n',
    },
    'javascript': {
        'display_name': 'JavaScript',
        'version': 'Node 22',
        'command': ['node'],
        'file_extension': '.js',
        'template': '// JavaScript code here\nconsole.log("Hello, World!");\n',
    },
    'c': {
        'display_name': 'C',
        'version': 'GCC 13',
        'command': None,  # Compile then run
        'file_extension': '.c',
        'compile_command': ['gcc', '-o', '{output}', '{source}', '-lm'],
        'template': '#include <stdio.h>\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}\n',
    },
    'cpp': {
        'display_name': 'C++',
        'version': 'G++ 13',
        'command': None,
        'file_extension': '.cpp',
        'compile_command': ['g++', '-o', '{output}', '{source}', '-std=c++17'],
        'template': '#include <iostream>\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}\n',
    },
    'java': {
        'display_name': 'Java',
        'version': '21',
        'command': None,
        'file_extension': '.java',
        'compile_command': ['javac', '{source}'],
        'run_command': ['java', '-cp', '{dir}', 'Main'],
        'template': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
    },
    'go': {
        'display_name': 'Go',
        'version': '1.22',
        'command': ['go', 'run'],
        'file_extension': '.go',
        'template': 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello, World!")\n}\n',
    },
}


# Models
class ExecutionRequest(BaseModel):
    code: str = Field(..., max_length=MAX_CODE_SIZE, description="Source code to execute")
    language: str = Field(default='python', description="Programming language")
    stdin: str = Field(default='', description="Standard input")
    timeout: int = Field(default=DEFAULT_TIMEOUT, ge=1, le=30, description="Timeout in seconds")
    max_output_size: int = Field(default=MAX_OUTPUT_SIZE, ge=100, le=100000)


class ExecutionResponse(BaseModel):
    success: bool
    output: str
    error: str
    execution_time_ms: int
    language: str
    memory_used_kb: Optional[int] = None


# Security
api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


# App
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Executor microservice starting up")
    yield
    logger.info("Executor microservice shutting down")


app = FastAPI(
    title="Code Executor Microservice",
    description="Isolated code execution service for the Online Compiler platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _execute_interpreted(code: str, language: str, stdin: str, timeout: int, max_output: int) -> dict:
    """Execute interpreted languages (Python, JS, Go)."""
    lang_config = LANGUAGES[language]

    with tempfile.NamedTemporaryFile(
        mode='w', suffix=lang_config['file_extension'], delete=False, dir=tempfile.gettempdir()
    ) as f:
        f.write(code)
        source_file = f.name

    try:
        cmd = lang_config['command'] + [source_file]
        start = time.time()

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tempfile.gettempdir(),
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin.encode() if stdin else None),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return {
                'success': False,
                'output': '',
                'error': f'Execution timed out after {timeout} seconds',
                'execution_time_ms': timeout * 1000,
            }

        elapsed_ms = int((time.time() - start) * 1000)
        output = stdout.decode('utf-8', errors='replace')[:max_output]
        error = stderr.decode('utf-8', errors='replace')[:max_output]

        return {
            'success': proc.returncode == 0,
            'output': output,
            'error': error if proc.returncode != 0 else '',
            'execution_time_ms': elapsed_ms,
        }
    finally:
        try:
            os.unlink(source_file)
        except OSError:
            pass


async def _execute_compiled(code: str, language: str, stdin: str, timeout: int, max_output: int) -> dict:
    """Execute compiled languages (C, C++, Java)."""
    lang_config = LANGUAGES[language]

    with tempfile.TemporaryDirectory() as tmpdir:
        if language == 'java':
            source_file = os.path.join(tmpdir, f'Main{lang_config["file_extension"]}')
        else:
            source_file = os.path.join(tmpdir, f'code{lang_config["file_extension"]}')

        output_file = os.path.join(tmpdir, 'code')

        with open(source_file, 'w') as f:
            f.write(code)

        # Compile
        compile_cmd = [
            c.format(source=source_file, output=output_file, dir=tmpdir)
            for c in lang_config['compile_command']
        ]

        try:
            compile_proc = await asyncio.create_subprocess_exec(
                *compile_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir,
            )
            stdout, stderr = await asyncio.wait_for(compile_proc.communicate(), timeout=30)

            if compile_proc.returncode != 0:
                return {
                    'success': False,
                    'output': '',
                    'error': f'Compilation Error:\n{stderr.decode("utf-8", errors="replace")}',
                    'execution_time_ms': 0,
                }
        except asyncio.TimeoutError:
            return {
                'success': False, 'output': '', 'error': 'Compilation timed out',
                'execution_time_ms': 0,
            }

        # Run
        if language == 'java':
            run_cmd = [c.format(dir=tmpdir) for c in lang_config['run_command']]
        else:
            run_cmd = [output_file]

        start = time.time()
        try:
            run_proc = await asyncio.create_subprocess_exec(
                *run_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir,
            )
            stdout, stderr = await asyncio.wait_for(
                run_proc.communicate(input=stdin.encode() if stdin else None),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            return {
                'success': False, 'output': '',
                'error': f'Execution timed out after {timeout} seconds',
                'execution_time_ms': timeout * 1000,
            }

        elapsed_ms = int((time.time() - start) * 1000)

        return {
            'success': run_proc.returncode == 0,
            'output': stdout.decode('utf-8', errors='replace')[:max_output],
            'error': stderr.decode('utf-8', errors='replace')[:max_output] if run_proc.returncode != 0 else '',
            'execution_time_ms': elapsed_ms,
        }


@app.post("/execute", response_model=ExecutionResponse)
async def execute(req: ExecutionRequest, api_key: str = Depends(verify_api_key)):
    """Execute code in a sandboxed environment."""
    if req.language not in LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.language}")

    logger.info(f"Executing {req.language} code ({len(req.code)} chars)")

    lang_config = LANGUAGES[req.language]

    if lang_config.get('command'):
        result = await _execute_interpreted(req.code, req.language, req.stdin, req.timeout, req.max_output_size)
    else:
        result = await _execute_compiled(req.code, req.language, req.stdin, req.timeout, req.max_output_size)

    return ExecutionResponse(
        success=result['success'],
        output=result['output'],
        error=result['error'],
        execution_time_ms=result['execution_time_ms'],
        language=req.language,
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "executor", "version": "2.0.0"}


@app.get("/languages")
async def languages(api_key: str = Depends(verify_api_key)):
    return [
        {
            'name': name,
            'display_name': config['display_name'],
            'version': config['version'],
            'template': config.get('template', ''),
        }
        for name, config in LANGUAGES.items()
    ]
