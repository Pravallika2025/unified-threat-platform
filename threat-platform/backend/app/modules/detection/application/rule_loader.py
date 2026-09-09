"""Loads YAML detection rules from detection-content/ and validates their shape.

Rules are data. Adding a detection should not require a Python change or a redeploy.
"""

import logging
from pathlib import Path

import yaml

from app.core.config import settings
from app.modules.detection.domain.entities import DetectionRule, RuleType, Severity

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {"id", "title", "severity", "logic"}


class RuleLoader:
    def __init__(self, content_dir: Path | None = None):
        self.content_dir = content_dir or settings.detection_content_dir
        self._cache: list[DetectionRule] | None = None

    def load_all(self, *, force: bool = False) -> list[DetectionRule]:
        if self._cache is not None and not force:
            return self._cache

        rules_dir = self.content_dir / "rules"
        rules: list[DetectionRule] = []

        if not rules_dir.exists():
            logger.warning("Detection content directory not found: %s", rules_dir)
            self._cache = []
            return self._cache

        for path in sorted(rules_dir.rglob("*.yml")) + sorted(rules_dir.rglob("*.yaml")):
            try:
                rules.extend(self._load_file(path))
            except Exception:
                logger.exception("Skipping malformed rule file %s", path)

        logger.info("Loaded %d detection rules from %s", len(rules), rules_dir)
        self._cache = rules
        return rules

    def _load_file(self, path: Path) -> list[DetectionRule]:
        with path.open() as fh:
            docs = [d for d in yaml.safe_load_all(fh) if d]

        loaded = []
        for doc in docs:
            missing = REQUIRED_KEYS - doc.keys()
            if missing:
                logger.error("Rule in %s missing keys: %s", path.name, missing)
                continue
            logic = doc["logic"]
            loaded.append(
                DetectionRule(
                    id=doc["id"],
                    title=doc["title"],
                    description=doc.get("description", ""),
                    severity=Severity(doc["severity"]),
                    rule_type=RuleType(logic.get("type", "match")),
                    source_types=doc.get("source_types", ["all"]),
                    environments=doc.get("environments", ["all"]),
                    logic=logic,
                    attack=doc.get("attack", {}),
                    risk=doc.get("risk", {}),
                    response_suggestions=doc.get("response_suggestions", []),
                    enabled=doc.get("enabled", True),
                )
            )
        return loaded

    def reload(self) -> int:
        return len(self.load_all(force=True))


rule_loader = RuleLoader()
