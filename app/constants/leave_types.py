LEAVE_TYPE_CHOICES = ("paid", "casual_sick", "floater")

LEAVE_TYPE_LABELS = {
    "paid": "Paid Leave",
    "casual_sick": "Casual/Sick Leave",
    "floater": "Floater Leave",
}

# Legacy values are still accepted so existing records continue to sync safely.
LEGACY_LEAVE_TYPE_ALIASES = {
    "vacation": "paid",
    "casual": "casual_sick",
    "sick": "casual_sick",
    "personal": "floater",
    "emergency": "floater",
}

RAZORPAY_LEAVE_TYPE_IDS = {
    "paid": 0,
    "casual_sick": 1,
    "floater": 2,
}


def normalize_leave_type(leave_type: str) -> str:
    normalized = (leave_type or "").strip().lower().replace("-", "_").replace(" ", "_")
    return LEGACY_LEAVE_TYPE_ALIASES.get(normalized, normalized)


def get_leave_type_label(leave_type: str) -> str:
    normalized = normalize_leave_type(leave_type)
    return LEAVE_TYPE_LABELS.get(normalized, normalized.replace("_", " ").title())
