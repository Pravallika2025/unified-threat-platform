"""Vendor field name -> canonical field name.

Extend this dict rather than writing per-vendor branching in the normalizer.
"""

FIELD_ALIASES: dict[str, str] = {
    # source ip
    "src_ip": "source_ip", "srcip": "source_ip", "sourceip": "source_ip",
    "client_ip": "source_ip", "ip": "source_ip", "remote_addr": "source_ip",
    # destination
    "dst_ip": "destination_ip", "dstip": "destination_ip", "dest_ip": "destination_ip",
    "destinationip": "destination_ip", "target_ip": "destination_ip",
    "dst_port": "destination_port", "dport": "destination_port", "port": "destination_port",
    # identity
    "username": "user_name", "user": "user_name", "account": "user_name",
    "accountname": "user_name", "userid": "user_name", "principal": "user_name",
    # host
    "hostname": "host_name", "host": "host_name", "computer": "host_name",
    "device_name": "host_name", "machine": "host_name",
    # action / outcome
    "action": "event_action", "eventtype": "event_action", "event_name": "event_action",
    "activity": "event_action", "operation": "event_action",
    "result": "event_outcome", "status": "event_outcome", "outcome": "event_outcome",
    # misc
    "proc": "process_name", "process": "process_name", "image": "process_name",
    "sha256": "file_hash", "hash": "file_hash", "md5": "file_hash",
    "bytes_sent": "bytes_out", "out_bytes": "bytes_out", "bytes": "bytes_out",
    "msg": "message", "description": "message", "text": "message",
    "@timestamp": "timestamp", "time": "timestamp", "event_time": "timestamp",
    "date": "timestamp", "ts": "timestamp",
}

SUCCESS_VALUES = {"success", "succeeded", "ok", "allow", "allowed", "accept", "0", "true"}
FAILURE_VALUES = {"failure", "failed", "fail", "deny", "denied", "block", "blocked", "error"}


def canonical_key(key: str) -> str:
    normalized = key.strip().lower().replace("-", "_").replace(" ", "_")
    return FIELD_ALIASES.get(normalized, normalized)


def canonical_outcome(value: str | None) -> str | None:
    if value is None:
        return None
    v = str(value).strip().lower()
    if v in SUCCESS_VALUES:
        return "success"
    if v in FAILURE_VALUES:
        return "failure"
    return "unknown"
