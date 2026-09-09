"""Statistical baseline detection.

TODO: implement. Suggested first pass — rolling 7-day mean/stddev per
(environment_id, event_action, hour_of_day); flag values beyond 3 sigma.
Keep the baseline in its own table so findings stay explainable to an analyst.
"""

from typing import Any

from app.modules.detection.domain.entities import Finding


class AnomalyEngine:
    def evaluate(self, events: list[Any]) -> list[Finding]:
        return []
