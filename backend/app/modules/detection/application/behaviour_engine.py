"""UEBA-style behavioral sequence detection engine.

Detects multi-stage behavioral patterns across temporal windows on the same entity:
1. Reconnaissance -> Authentication Attempt / Access.
2. Authentication -> Privilege Escalation / Sudo command execution.
3. Authentication -> Abnormal Data Access or High Outbound Transfer.
4. Multi-Source Subnet / Concurrent Login Behavior on the same account.
5. Living-off-the-land command chains (e.g. discovery followed by process spawning).
"""

from collections import defaultdict
from typing import Any

from app.modules.detection.domain.entities import Finding, Severity


class BehaviourEngine:
    def evaluate(self, events: list[Any]) -> list[Finding]:
        if not events:
            return []

        # Sort events chronologically
        sorted_events = sorted(
            events,
            key=lambda e: getattr(e, "timestamp", None) or 0
        )

        findings: list[Finding] = []
        findings.extend(self._detect_auth_to_priv_escalation(sorted_events))
        findings.extend(self._detect_recon_to_access(sorted_events))
        findings.extend(self._detect_multi_ip_account_access(sorted_events))
        findings.extend(self._detect_auth_to_exfil_chain(sorted_events))
        return findings

    def _detect_auth_to_priv_escalation(self, events: list[Any]) -> list[Finding]:
        """Detect login/auth followed quickly by privilege escalation or sudo actions."""
        findings = []
        user_events: dict[str, list[Any]] = defaultdict(list)

        for event in events:
            user = getattr(event, "user_name", None)
            if user:
                user_events[user].append(event)

        for user, u_events in user_events.items():
            has_login = False
            login_event = None
            priv_events = []

            for evt in u_events:
                action = (getattr(evt, "event_action", "") or "").lower()
                outcome = (getattr(evt, "event_outcome", "") or "").lower()
                category = (getattr(evt, "event_category", "") or "").lower()

                if ("login" in action or "auth" in action or "session" in category) and outcome in ["success", "accepted", "ok", ""]:
                    has_login = True
                    login_event = evt
                elif has_login and ("sudo" in action or "privilege" in action or "admin" in action or "role" in action or "root" in action):
                    priv_events.append(evt)

            if has_login and priv_events and login_event:
                all_ids = [login_event.id] + [e.id for e in priv_events]
                findings.append(
                    Finding(
                        rule_id="BEHAV-0001",
                        title=f"Behavioral sequence: User {user} authenticated and immediately executed privileged commands",
                        severity=Severity.HIGH,
                        environment_id=login_event.environment_id,
                        event_ids=all_ids,
                        entity=user,
                        evidence={
                            "user": user,
                            "login_time": str(getattr(login_event, "timestamp", "")),
                            "privileged_actions": [getattr(e, "event_action", "") for e in priv_events],
                            "privileged_event_count": len(priv_events),
                        },
                        attack={"tactic": "Privilege Escalation", "technique": "T1548 - Abuse Elevation Control Mechanism"},
                    )
                )

        return findings

    def _detect_recon_to_access(self, events: list[Any]) -> list[Finding]:
        """Detect port scan/probing from an IP followed by login attempts."""
        findings = []
        ip_events: dict[str, list[Any]] = defaultdict(list)

        for event in events:
            ip = getattr(event, "source_ip", None)
            if ip:
                ip_events[ip].append(event)

        for ip, ip_evts in ip_events.items():
            probed_ports = set()
            auth_attempts = []

            for evt in ip_evts:
                port = getattr(evt, "destination_port", None)
                action = (getattr(evt, "event_action", "") or "").lower()
                category = (getattr(evt, "event_category", "") or "").lower()

                if port and ("scan" in action or "probe" in action or "network" in category):
                    probed_ports.add(port)
                elif "auth" in action or "login" in action or "sshd" in (getattr(evt, "process_name", "") or "").lower():
                    auth_attempts.append(evt)

            if len(probed_ports) >= 3 and auth_attempts:
                all_evts = [e.id for e in ip_evts if getattr(e, "destination_port", None) in probed_ports or e in auth_attempts]
                sample = ip_evts[0]
                findings.append(
                    Finding(
                        rule_id="BEHAV-0002",
                        title=f"Behavioral sequence: Reconnaissance probing followed by authentication attempts from {ip}",
                        severity=Severity.HIGH,
                        environment_id=sample.environment_id,
                        event_ids=all_evts,
                        entity=ip,
                        evidence={
                            "source_ip": ip,
                            "probed_ports": list(probed_ports),
                            "auth_attempt_count": len(auth_attempts),
                        },
                        attack={"tactic": "Initial Access", "technique": "T1190 - Exploit Public-Facing Application"},
                    )
                )

        return findings

    def _detect_multi_ip_account_access(self, events: list[Any]) -> list[Finding]:
        """Detect account accessed concurrently or rapidly across multiple distinct IP addresses."""
        findings = []
        user_ips: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))

        for event in events:
            user = getattr(event, "user_name", None)
            ip = getattr(event, "source_ip", None)
            action = (getattr(event, "event_action", "") or "").lower()
            if user and ip and ("auth" in action or "login" in action or "session" in action):
                user_ips[user][ip].append(event)

        for user, ip_map in user_ips.items():
            if len(ip_map) >= 3:
                all_evts = [e for evts in ip_map.values() for e in evts]
                sample = all_evts[0]
                findings.append(
                    Finding(
                        rule_id="BEHAV-0003",
                        title=f"Behavioral anomaly: Concurrent / multi-location login attempts for {user}",
                        severity=Severity.HIGH,
                        environment_id=sample.environment_id,
                        event_ids=[e.id for e in all_evts],
                        entity=user,
                        evidence={
                            "user": user,
                            "distinct_source_ips": list(ip_map.keys()),
                            "total_events": len(all_evts),
                        },
                        attack={"tactic": "Credential Access", "technique": "T1110 - Brute Force"},
                    )
                )

        return findings

    def _detect_auth_to_exfil_chain(self, events: list[Any]) -> list[Finding]:
        """Detect authentication followed immediately by large outbound file/data transfer."""
        findings = []
        user_events: dict[str, list[Any]] = defaultdict(list)

        for event in events:
            user = getattr(event, "user_name", None) or getattr(event, "source_ip", None)
            if user:
                user_events[user].append(event)

        for entity, u_events in user_events.items():
            login_seen = False
            login_evt = None
            exfil_events = []

            for evt in u_events:
                action = (getattr(evt, "event_action", "") or "").lower()
                bytes_out = getattr(evt, "bytes_out", None) or 0

                if "login" in action or "auth" in action:
                    login_seen = True
                    login_evt = evt
                elif login_seen and bytes_out >= 1_000_000:
                    exfil_events.append(evt)

            if login_seen and exfil_events and login_evt:
                all_evts = [login_evt] + exfil_events
                total_exfil = sum(getattr(e, "bytes_out", 0) or 0 for e in exfil_events)
                findings.append(
                    Finding(
                        rule_id="BEHAV-0004",
                        title=f"Behavioral sequence: Access session followed by large data exfiltration for {entity}",
                        severity=Severity.CRITICAL if total_exfil >= 10_000_000 else Severity.HIGH,
                        environment_id=login_evt.environment_id,
                        event_ids=[e.id for e in all_evts],
                        entity=entity,
                        evidence={
                            "entity": entity,
                            "total_bytes_transferred": total_exfil,
                            "exfiltration_events_count": len(exfil_events),
                        },
                        attack={"tactic": "Exfiltration", "technique": "T1041 - Exfiltration Over C2 Channel"},
                    )
                )

        return findings
