from app.modules.normalization.domain.field_map import canonical_key, canonical_outcome
from app.modules.normalization.infrastructure.parsers.json_parser import JsonParser
from app.modules.normalization.infrastructure.parsers.syslog_parser import SyslogParser


def test_vendor_field_names_map_to_canonical():
    assert canonical_key("src_ip") == "source_ip"
    assert canonical_key("SrcIP") == "source_ip"
    assert canonical_key("username") == "user_name"


def test_outcome_values_normalize():
    assert canonical_outcome("Failed") == "failure"
    assert canonical_outcome("ALLOW") == "success"
    assert canonical_outcome("weird") == "unknown"


def test_syslog_parser_extracts_ssh_failure():
    line = "Jan  1 10:00:00 host sshd[1]: Failed password for invalid user admin from 203.0.113.5 port 22 ssh2"
    parsed = SyslogParser().parse({"raw": line})
    assert parsed["source_ip"] == "203.0.113.5"
    assert parsed["event_action"] == "login_failed"
    assert parsed["event_outcome"] == "failure"


def test_json_parser_flattens_nested_fields():
    parsed = JsonParser().parse({"source": {"ip": "10.0.0.1"}, "user": "alice"})
    assert parsed["user_name"] == "alice"
    assert parsed.get("source_ip") == "10.0.0.1"
