"""RBAC matrix — section 6 of the project charter.

Single source of truth. The frontend mirrors this in src/lib/rbac/permissions.ts.
"""

from enum import StrEnum


class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    SECURITY_ANALYST = "security_analyst"
    ENVIRONMENT_USER = "environment_user"


class Permission(StrEnum):
    # Environments
    ENV_MANAGE = "environment.manage"
    ENV_VIEW = "environment.view"
    # Users & roles
    USER_MANAGE = "user.manage"
    USER_VIEW = "user.view"
    # Settings
    SETTINGS_MANAGE = "settings.manage"
    # Data
    DATA_UPLOAD = "data.upload"
    DATA_VIEW = "data.view"
    # Alerts & incidents
    ALERT_VIEW = "alert.view"
    INCIDENT_VIEW = "incident.view"
    INCIDENT_VIEW_OWN = "incident.view_own"
    INCIDENT_INVESTIGATE = "incident.investigate"
    INCIDENT_ASSIGN = "incident.assign"
    INCIDENT_SEVERITY = "incident.set_severity"
    # Decisions & response
    DECISION_RECOMMEND = "decision.recommend"
    DECISION_APPROVE = "decision.approve"
    RESPONSE_EXECUTE = "response.execute"
    # Reports & audit
    REPORT_GENERATE = "report.generate"
    REPORT_VIEW = "report.view"
    AUDIT_VIEW = "audit.view"
    REQUEST_RAISE = "request.raise"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.SECURITY_ANALYST: {
        Permission.ENV_VIEW,
        Permission.USER_VIEW,
        Permission.DATA_VIEW,
        Permission.ALERT_VIEW,
        Permission.INCIDENT_VIEW,
        Permission.INCIDENT_INVESTIGATE,
        Permission.INCIDENT_ASSIGN,
        Permission.INCIDENT_SEVERITY,
        Permission.DECISION_RECOMMEND,
        Permission.REPORT_GENERATE,
        Permission.REPORT_VIEW,
        Permission.AUDIT_VIEW,
    },
    Role.ENVIRONMENT_USER: {
        Permission.ENV_VIEW,
        Permission.DATA_UPLOAD,
        Permission.DATA_VIEW,
        Permission.INCIDENT_VIEW_OWN,
        Permission.REPORT_VIEW,
        Permission.REQUEST_RAISE,
    },
}


def permissions_for(role: Role) -> set[Permission]:
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in permissions_for(role)
