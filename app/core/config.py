from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "scada-llm-security"
    log_level: str = "INFO"

    classifier_url: str = "http://127.0.0.1:8001"
    classifier_endpoint: str = "/classify"

    qwen_url: str = "http://127.0.0.1:8002"
    qwen_endpoint: str = "/chat"

    request_timeout_seconds: float = 30.0
    rules_path: Path = Path("./app/rules")
    audit_log_path: Path = Path("./app/logs/audit.jsonl")
