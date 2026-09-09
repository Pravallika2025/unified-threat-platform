from enum import StrEnum


class EnvironmentType(StrEnum):
    COLLEGE = "college"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    ENTERPRISE = "enterprise"
    AIRPORT = "airport"
    GOVERNMENT = "government"
    CUSTOM = "custom"


class EnvironmentStatus(StrEnum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
