"""Orders a cluster's tactics and alerts into an attack narrative for the incident timeline.

Transforms correlated alerts into an ordered, chronological and MITRE ATT&CK
aligned incident storyline with tactical stage descriptions and recommendations.
"""

from typing import Any

from app.modules.correlation.domain.entities import (
    KILL_CHAIN_ORDER,
    TACTIC_NAMES,
    KillChainNarrative,
    KillChainStage,
    resolve_tactic_id,
)
from app.shared.types import as_utc


class KillChainBuilder:
    def build_narrative(self, alerts: list[Any], entity: str) -> KillChainNarrative:
        if not alerts:
            return KillChainNarrative(
                entity=entity,
                stages=[],
                unique_tactics_count=0,
                is_progressive=False,
                summary=f"No active threat sequence observed for {entity}.",
                recommended_action="Continue baseline monitoring.",
            )

        # Sort chronologically
        sorted_alerts = sorted(alerts, key=lambda a: as_utc(getattr(a, "created_at", None)))

        stages: list[KillChainStage] = []
        observed_tactic_ids: list[str] = []

        for idx, alert in enumerate(sorted_alerts, start=1):
            tactic_raw = getattr(alert, "attack_tactic", None)
            tactic_id = resolve_tactic_id(tactic_raw) or "TA0001"
            tactic_name = TACTIC_NAMES.get(tactic_id, tactic_raw or "General Activity")
            observed_tactic_ids.append(tactic_id)

            stage = KillChainStage(
                stage_number=idx,
                tactic_id=tactic_id,
                tactic_name=tactic_name,
                technique=getattr(alert, "attack_technique", None),
                alert_id=alert.id,
                alert_title=getattr(alert, "title", "Threat Alert"),
                severity=getattr(alert, "severity", "medium"),
                entity=getattr(alert, "entity", entity),
                timestamp=as_utc(getattr(alert, "created_at", None)),
                evidence=getattr(alert, "evidence", {}) or {},
            )
            stages.append(stage)

        # Check if indices progress sequentially along the kill chain
        order_indices = [KILL_CHAIN_ORDER.index(tid) for tid in observed_tactic_ids if tid in KILL_CHAIN_ORDER]
        is_progressive = len(set(order_indices)) >= 2 and order_indices == sorted(order_indices)

        # Build narrative summary
        tactic_flow = " ➔ ".join([s.tactic_name for s in stages])
        unique_tactics = len(set(observed_tactic_ids))

        if is_progressive:
            summary = (
                f"Multi-stage progressive kill chain detected for {entity} across {len(stages)} alerts. "
                f"Attack progression: {tactic_flow}."
            )
            rec_action = (
                "Isolate affected endpoint/host immediately and revoke active session credentials. "
                "Initiate lateral movement investigation."
            )
        elif unique_tactics > 1:
            summary = (
                f"Correlated multi-tactic attack activity observed for {entity}. "
                f"Tactics engaged: {', '.join(set(s.tactic_name for s in stages))}."
            )
            rec_action = "Review access logs and block attacking IP at perimeter firewall."
        else:
            summary = f"Repeated single-tactic alerts targeting {entity}: {stages[0].tactic_name}."
            rec_action = "Evaluate rate-limiting and verify authentication posture."

        return KillChainNarrative(
            entity=entity,
            stages=stages,
            unique_tactics_count=unique_tactics,
            is_progressive=is_progressive,
            summary=summary,
            recommended_action=rec_action,
        )
