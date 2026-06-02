import asyncio
import logging
from pathlib import Path
from typing import Any

from app.schemas.classification import ClassificationResult

logger = logging.getLogger(__name__)


class RobertaClassifier:
    REQUIRED_FILES = ("config.json", "tokenizer.json", "tokenizer_config.json")
    REQUIRED_WEIGHT_OPTIONS = ("model.safetensors", "pytorch_model.bin")

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.loaded = False
        self.error: str | None = None
        self._pipeline: Any | None = None
        self._validate_and_load()

    def _validate_and_load(self) -> None:
        missing = self._missing_files()
        if missing:
            self.error = f"Missing {', '.join(missing)}"
            logger.error("RoBERTa service degraded: %s", self.error)
            return

        try:
            from transformers import pipeline

            self._pipeline = pipeline(
                "text-classification",
                model=str(self.model_path),
                tokenizer=str(self.model_path),
                top_k=None,
            )
            self.loaded = True
            logger.info("RoBERTa model loaded from %s", self.model_path)
        except Exception as exc:
            self.error = f"Model load failed: {exc}"
            logger.exception("RoBERTa service degraded")

    def _missing_files(self) -> list[str]:
        missing: list[str] = []
        if not self.model_path.exists():
            return [str(self.model_path)]
        for filename in self.REQUIRED_FILES:
            if not (self.model_path / filename).exists():
                missing.append(filename)
        if not any((self.model_path / filename).exists() for filename in self.REQUIRED_WEIGHT_OPTIONS):
            missing.append("model.safetensors or pytorch_model.bin")
        return missing

    async def classify(self, text: str) -> ClassificationResult:
        result = await asyncio.to_thread(self._classify_sync, text)
        return result

    def _classify_sync(self, text: str) -> ClassificationResult:
        if self._pipeline is None:
            return ClassificationResult(label="suspicious", score=0.0)

        raw = self._pipeline(text)
        candidates = raw[0] if raw and isinstance(raw[0], list) else raw
        best = max(candidates, key=lambda item: float(item["score"]))
        label = normalize_label(str(best["label"]))
        return ClassificationResult(label=label, score=round(float(best["score"]), 6))


def normalize_label(label: str) -> str:
    normalized = label.lower().replace("label_", "")
    mapping = {
        "0": "safe",
        "1": "suspicious",
        "2": "malicious",
        "safe": "safe",
        "suspicious": "suspicious",
        "malicious": "malicious",
    }
    return mapping.get(normalized, "suspicious")

