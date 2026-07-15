from functools import lru_cache

from app.core.config import Settings
from app.services.audit_service import AuditService
from app.services.qwen_client import QwenClient
from app.services.classifier_client import ClassifierClient
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
def get_classifier_client() -> ClassifierClient:
    settings = get_settings()
    return ClassifierClient(
        base_url=settings.classifier_url,
        endpoint=settings.classifier_endpoint,
        timeout_seconds=settings.request_timeout_seconds,
    )


@lru_cache
def get_qwen_client() -> QwenClient:
    settings = get_settings()
    return QwenClient(
        base_url=settings.qwen_url,
        endpoint=settings.qwen_endpoint,
        timeout_seconds=settings.request_timeout_seconds,
    )
