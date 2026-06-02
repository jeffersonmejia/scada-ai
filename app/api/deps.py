from functools import lru_cache

from app.core.config import Settings
from app.services.audit_service import AuditService
from app.services.ollama_client import OllamaClient
from app.services.roberta_client import RobertaClient
from app.services.roberta_service import RobertaClassifier
from app.services.rule_engine import RuleEngine


def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_rule_engine() -> RuleEngine:
    settings = get_settings()
    return RuleEngine(settings.rules_path)


@lru_cache
def get_audit_service() -> AuditService:
    settings = get_settings()
    return AuditService(settings.audit_log_path)


@lru_cache
def get_roberta_client() -> RobertaClient:
    settings = get_settings()
    return RobertaClient(settings.roberta_url, settings.request_timeout_seconds)


@lru_cache
def get_ollama_client() -> OllamaClient:
    settings = get_settings()
    return OllamaClient(
        base_url=settings.ollama_url,
        model=settings.ollama_model,
        timeout_seconds=settings.request_timeout_seconds,
    )


@lru_cache
def get_roberta_classifier() -> RobertaClassifier:
    settings = get_settings()
    return RobertaClassifier(settings.roberta_model_path)
