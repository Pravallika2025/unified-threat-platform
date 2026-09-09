import pytest

from app.core.exceptions import PermissionDeniedError
from app.modules.ingestion.application.consent_guard import ConsentGuard
from app.modules.ingestion.domain.source_type import SourceType


def test_authorized_source_is_allowed():
    ConsentGuard(["firewall", "vpn"]).assert_allowed(SourceType.FIREWALL, "Test Env")


def test_unauthorized_source_is_rejected():
    with pytest.raises(PermissionDeniedError):
        ConsentGuard(["firewall"]).assert_allowed(SourceType.EDR, "Test Env")


def test_empty_authorization_rejects_everything():
    with pytest.raises(PermissionDeniedError):
        ConsentGuard([]).assert_allowed(SourceType.FIREWALL, "Test Env")


def test_wildcard_allows_all():
    ConsentGuard(["all"]).assert_allowed(SourceType.EDR, "Test Env")
