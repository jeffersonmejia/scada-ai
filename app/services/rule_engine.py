import json
import logging
import re
from pathlib import Path

from app.models.rule import Rule
from app.schemas.classification import ClassificationResult

logger = logging.getLogger(__name__)


class RuleDecision:
    def __init__(self, blocked: bool, triggered_rules: list[str], message: str) -> None:
        self.blocked = blocked
        self.triggered_rules = triggered_rules
        self.message = message


class RuleEngine:
    def __init__(self, rules_path: Path) -> None:
        self.rules_path = rules_path
        self.input_rules = self._load_many(
            "protocols.json",
            "substations.json",
            "control_centers.json",
            "input_rules.json",
            "malicious_patterns.json",
        )
        self.output_rules = self._load_many("output_rules.json", "malicious_patterns.json")

    def validate_input(self, prompt: str, classification: ClassificationResult) -> RuleDecision:
        triggered = self._match(prompt, self.input_rules)
        blocked = classification.label == "malicious" or any(rule.decision == "block" for rule in triggered)
        if classification.label == "suspicious" and any(rule.severity == "high" for rule in triggered):
            blocked = True
        message = "Solicitud bloqueada por políticas de seguridad SCADA." if blocked else "Solicitud permitida."
        return RuleDecision(blocked, [rule.id for rule in triggered], message)

    def validate_output(self, response: str) -> RuleDecision:
        triggered = self._match(response, self.output_rules)
        blocked = any(rule.decision == "block" for rule in triggered)
        message = "Respuesta bloqueada por políticas de salida." if blocked else "Respuesta permitida."
        return RuleDecision(blocked, [rule.id for rule in triggered], message)

    def _load_many(self, *filenames: str) -> list[Rule]:
        rules: list[Rule] = []
        for filename in filenames:
            rules.extend(self._load_file(filename))
        return rules

    def _load_file(self, filename: str) -> list[Rule]:
        path = self.rules_path / filename
        if not path.exists():
            logger.error("Rules file missing: %s", path)
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return [Rule.model_validate(item) for item in data.get("rules", [])]
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            logger.error("Cannot load rules from %s: %s", path, exc)
            return []

    def _match(self, text: str, rules: list[Rule]) -> list[Rule]:
        matched: list[Rule] = []
        for rule in rules:
            for pattern in rule.patterns:
                if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                    matched.append(rule)
                    break
        return matched

