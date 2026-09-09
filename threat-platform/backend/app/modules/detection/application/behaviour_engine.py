"""UEBA-style sequence detection (recon -> access -> exfil on the same entity).

TODO: implement on top of correlation/kill_chain_builder.py once enough
event volume exists to build per-user baselines.
"""

from typing import Any

from app.modules.detection.domain.entities import Finding


class BehaviourEngine:
    def evaluate(self, events: list[Any]) -> list[Finding]:
        return []
