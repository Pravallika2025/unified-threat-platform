"""Pure authorisation policy. No framework, no DB."""

from app.core.security.permissions import Permission, Role, has_permission

MIN_PASSWORD_LENGTH = 10


def can_manage_user(actor_role: Role, target_role: Role) -> bool:
    if not has_permission(actor_role, Permission.USER_MANAGE):
        return False
    # Only a super admin may create or modify another super admin.
    if target_role == Role.SUPER_ADMIN:
        return actor_role == Role.SUPER_ADMIN
    return True


def password_meets_policy(password: str) -> tuple[bool, str]:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    if password.isalpha() or password.isdigit():
        return False, "Password must mix letters, digits and symbols"
    return True, ""


def can_access_environment(role: Role, user_env: str | None, target_env: str | None) -> bool:
    if role in (Role.SUPER_ADMIN, Role.SECURITY_ANALYST):
        return True
    return target_env is not None and user_env == target_env
