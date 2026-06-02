from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_role: Literal["middleware", "classifier"] = "middleware"
    app_name: str = "scada-llm-security"
    log_level: str = "INFO"

    roberta_model_path: Path = Path("./models/roberta_scada")
    roberta_url: str = "http://127.0.0.1:8001"

    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "mistral:7b-instruct-v0.3-q8_0"

    api_key: SecretStr = Field(default=SecretStr("change_me"))
    request_timeout_seconds: float = 30.0
    rules_path: Path = Path("./app/rules")
    audit_log_path: Path = Path("./app/logs/audit.jsonl")

