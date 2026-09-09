"""Environments created on first run so the app is usable immediately."""

SEED_ENVIRONMENTS = [
    {
        "name": "Central University Network",
        "type": "college",
        "description": "Campus-wide network, student and staff systems",
        "authorized_sources": [
            "firewall", "vpn", "windows_security", "linux_auth", "user_upload"
        ],
    },
    {
        "name": "City General Hospital",
        "type": "hospital",
        "description": "Clinical and administrative network segments",
        "authorized_sources": [
            "firewall", "edr", "windows_security", "email_security", "user_upload"
        ],
    },
    {
        "name": "Corporate HQ",
        "type": "enterprise",
        "description": "Head office and remote workforce",
        "authorized_sources": [
            "firewall", "vpn", "edr", "aws_cloudtrail", "siem", "user_upload"
        ],
    },
]
