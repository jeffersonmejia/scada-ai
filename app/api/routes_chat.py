from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_audit_service, get_ollama_client, get_roberta_client, get_rule_engine
from app.schemas.audit import AuditEvent
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.classification import ClassificationResult
from app.security.api_key import require_api_key
from app.services.audit_service import AuditService
from app.services.ollama_client import OllamaClient
from app.services.roberta_client import RobertaClient
from app.services.rule_engine import RuleEngine

router = APIRouter(prefix="/api", tags=["middleware"], dependencies=[Depends(require_api_key)])
web_router = APIRouter(prefix="/web", tags=["web-client"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    rules: RuleEngine = Depends(get_rule_engine),
    roberta: RobertaClient = Depends(get_roberta_client),
    ollama: OllamaClient = Depends(get_ollama_client),
    audit: AuditService = Depends(get_audit_service),
) -> ChatResponse:
    request_id = str(uuid4())
    total_start = perf_counter()

    classification_start = perf_counter()
    classification = await roberta.classify(payload.prompt, request_id)
    classification_ms = elapsed_ms(classification_start)

    validation_start = perf_counter()
    input_decision = rules.validate_input(payload.prompt, classification)
    validation_input_ms = elapsed_ms(validation_start)

    inference_ms = 0.0
    generated_response = ""
    output_rules: list[str] = []

    if input_decision.blocked:
        decision = "blocked_input"
        response_text = input_decision.message
    else:
        inference_start = perf_counter()
        generated_response = await ollama.generate(payload.prompt, request_id)
        inference_ms = elapsed_ms(inference_start)

        output_validation_start = perf_counter()
        output_decision = rules.validate_output(generated_response)
        validation_output_ms = elapsed_ms(output_validation_start)
        validation_input_ms += validation_output_ms
        output_rules = output_decision.triggered_rules

        if output_decision.blocked:
            decision = "blocked_output"
            response_text = output_decision.message
        else:
            decision = "allowed"
            response_text = generated_response

    total_ms = elapsed_ms(total_start)
    triggered_rules = input_decision.triggered_rules + output_rules

    await audit.record(
        AuditEvent(
            request_id=request_id,
            client_host=request.client.host if request.client else None,
            prompt=payload.prompt,
            roberta_label=classification.label,
            roberta_score=classification.score,
            triggered_rules=triggered_rules,
            final_decision=decision,
            generated_response=generated_response,
            classification_ms=classification_ms,
            inference_ms=inference_ms,
            validation_ms=validation_input_ms,
            total_ms=total_ms,
        )
    )

    return ChatResponse(
        request_id=request_id,
        decision=decision,
        classification=classification,
        triggered_rules=triggered_rules,
        response=response_text,
    )


@web_router.post("/chat", response_model=ChatResponse)
async def web_chat(
    payload: ChatRequest,
    request: Request,
    rules: RuleEngine = Depends(get_rule_engine),
    roberta: RobertaClient = Depends(get_roberta_client),
    ollama: OllamaClient = Depends(get_ollama_client),
    audit: AuditService = Depends(get_audit_service),
) -> ChatResponse:
    return await chat(payload, request, rules, roberta, ollama, audit)


def elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 3)
