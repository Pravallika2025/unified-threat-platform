from enum import StrEnum


class SourceType(StrEnum):
    FIREWALL = "firewall"
    IDS_IPS = "ids_ips"
    ROUTER = "router"
    VPN = "vpn"
    WINDOWS_SECURITY = "windows_security"
    LINUX_AUTH = "linux_auth"
    SERVER = "server"
    AWS_CLOUDTRAIL = "aws_cloudtrail"
    AZURE_ACTIVITY = "azure_activity"
    GCP_AUDIT = "gcp_audit"
    EDR = "edr"
    ANTIVIRUS = "antivirus"
    SIEM = "siem"
    WAF = "waf"
    EMAIL_SECURITY = "email_security"
    USER_ACTIVITY = "user_activity"
    THREAT_FEED = "threat_feed"
    USER_UPLOAD = "user_upload"
    API_INTEGRATION = "api_integration"
