from fastapi import APIRouter, Depends

from app.api.deps import get_roberta_classifier
from app.core.exceptions import ServiceUnavailableError
from app.schemas.classification import ClassificationRequest, ClassificationResult
from app.services.roberta_service import RobertaClassifier

router = APIRouter(tags=["classifier"])


@router.post("/classify", response_model=ClassificationResult)
async def classify(
    payload: ClassificationRequest,
    classifier: RobertaClassifier = Depends(get_roberta_classifier),
) -> ClassificationResult:
    if not classifier.loaded:
        raise ServiceUnavailableError(
            service="roberta",
            message="RoBERTa model not loaded",
        )
    return await classifier.classify(payload.text)

