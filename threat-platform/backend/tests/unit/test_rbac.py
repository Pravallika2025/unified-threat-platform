from app.core.security.permissions import Permission, Role, has_permission


def test_super_admin_has_everything():
    assert all(has_permission(Role.SUPER_ADMIN, p) for p in Permission)


def test_analyst_can_recommend_but_not_approve():
    """Separation of duties: the analyst who recommends a block cannot approve it."""
    assert has_permission(Role.SECURITY_ANALYST, Permission.DECISION_RECOMMEND)
    assert not has_permission(Role.SECURITY_ANALYST, Permission.DECISION_APPROVE)


def test_analyst_cannot_execute_response():
    assert not has_permission(Role.SECURITY_ANALYST, Permission.RESPONSE_EXECUTE)


def test_environment_user_cannot_see_all_incidents():
    assert not has_permission(Role.ENVIRONMENT_USER, Permission.INCIDENT_VIEW)
    assert has_permission(Role.ENVIRONMENT_USER, Permission.INCIDENT_VIEW_OWN)


def test_environment_user_cannot_manage_users():
    assert not has_permission(Role.ENVIRONMENT_USER, Permission.USER_MANAGE)
