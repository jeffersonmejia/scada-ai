from functools import lru_cache

from app.core.config import Settings
from app.services.audit_service import AuditService
from app.services.mistral_client import MistralClient
from app.services.roberta_client import RobertaClient
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
    return RobertaClient(
        base_url=settings.roberta_url,
        endpoint=settings.roberta_endpoint,
        timeout_seconds=settings.request_timeout_seconds,
    )


@lru_cache
def get_mistral_client() -> MistralClient:
    settings = get_settings()
    return MistralClient(
        base_url=settings.mistral_url,
        endpoint=settings.mistral_endpoint,
        timeout_seconds=settings.request_timeout_seconds,
    )
