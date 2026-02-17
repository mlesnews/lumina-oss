#!/usr/bin/env python3
"""PERSONAPLEX CodeLlama 13B Integration - KUBE Local LLM"""
import json, logging, time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import requests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskType(Enum):
    CODE_COMPLETION = "code_completion"
    CODE_EXPLANATION = "code_explanation"
    CODE_REFACTORING = "code_refactoring"

class ResponseFormat(Enum):
    TEXT = "text"
    JSON = "json"

@dataclass
class CodeAnalysisResult:
    task_id: str
    task_type: TaskType
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0

@dataclass
class CodeContext:
    code: str
    language: str
    file_path: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.1

    def to_prompt(self) -> str:
        return f"```{self.language}\n{self.code}\n```"

class CodeLlamaClient:
    DEFAULT_BASE_URL = "http://<NAS_PRIMARY_IP>:8000"
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout
        self._session = requests.Session()
        logger.info(f"CodeLlamaClient initialized: {self.base_url}")

    def health_check(self) -> bool:
        try:
            r = self._session.get(f"{self.base_url}/health", timeout=self.timeout)
            return r.status_code == 200
        except:
            return False

    def analyze_code(self, context: CodeContext, task_type: TaskType) -> CodeAnalysisResult:
        start = time.time()
        prompts = {
            TaskType.CODE_COMPLETION: f"Complete: {context.to_prompt()}",
            TaskType.CODE_EXPLANATION: f"Explain: {context.to_prompt()}",
            TaskType.CODE_REFACTORING: f"Refactor: {context.to_prompt()}",
        }
        payload = {"model": "codellama-13b", "prompt": prompts.get(task_type, ""), "max_tokens": context.max_tokens, "temperature": context.temperature}
        try:
            r = self._session.post(f"{self.base_url}/v1/completions", json=payload, timeout=self.timeout)
            r.raise_for_status()
            resp = r.json()
            choices = resp.get("choices", [])
            result = choices[0].get("text", "") if choices else ""
            return CodeAnalysisResult(task_id=f"task-{int(start*1000)}", task_type=task_type, success=True, result=result, processing_time_ms=(time.time()-start)*1000)
        except Exception as e:
            return CodeAnalysisResult(task_id=f"task-{int(start*1000)}", task_type=task_type, success=False, error=str(e))

    def complete_code(self, code: str, language: str) -> CodeAnalysisResult:
        return self.analyze_code(CodeContext(code=code, language=language), TaskType.CODE_COMPLETION)

def create_codellama_client(base_url: Optional[str] = None) -> CodeLlamaClient:
    return CodeLlamaClient(base_url=base_url)

if __name__ == "__main__":
    c = create_codellama_client()
    print(f"Health: {c.health_check()}")
    print("PERSONAPLEX CodeLlama Integration initialized!")
