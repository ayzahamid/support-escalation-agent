from langchain_core.tools import tool

_KNOWN_ISSUES = [
    {
        "id": "INC-2024-001",
        "title": "Mobile App Login Intermittent Failures",
        "status": "investigating",
        "services": ["mobile app", "login", "authentication", "app"],
        "description": (
            "Some customers experience login failures on the mobile app. "
            "Our engineering team is actively investigating. ETA: 2 hours."
        ),
        "started": "2024-01-15 08:00 UTC",
        "updated": "2024-01-15 10:30 UTC",
    },
    {
        "id": "INC-2024-002",
        "title": "Card Payment Processing Delays",
        "status": "monitoring",
        "services": ["card", "debit card", "credit card", "payment", "transaction", "pos"],
        "description": (
            "Card transactions may take longer than usual to process. "
            "Online and ACH payments are unaffected. Fix deployed; monitoring for stability."
        ),
        "started": "2024-01-14 22:00 UTC",
        "updated": "2024-01-15 09:00 UTC",
    },
    {
        "id": "MNT-2024-001",
        "title": "Scheduled Online Banking Maintenance",
        "status": "scheduled",
        "services": ["online banking", "web portal", "bill pay", "website"],
        "description": (
            "Planned maintenance for system upgrades. Online banking will be unavailable "
            "from 02:00–04:00 UTC on Jan 20."
        ),
        "started": "2024-01-20 02:00 UTC",
        "updated": "2024-01-20 04:00 UTC",
    },
]


@tool
def check_known_issues(service: str) -> str:
    """Check for active incidents or known technical issues affecting a specific banking service.
    Use this when a customer reports a technical problem (e.g., app not working, card declined)."""
    service_lower = service.lower()
    matches = [
        issue for issue in _KNOWN_ISSUES
        if any(svc in service_lower or service_lower in svc for svc in issue["services"])
    ]

    if not matches:
        return f"No known incidents found for '{service}'. The service appears to be operating normally."

    lines = [f"Found {len(matches)} active incident(s) for '{service}':"]
    for issue in matches:
        lines.append(
            f"\n  [{issue['status'].upper()}] {issue['title']} (ID: {issue['id']})\n"
            f"  {issue['description']}\n"
            f"  Last updated: {issue['updated']}"
        )
    return "\n".join(lines)
