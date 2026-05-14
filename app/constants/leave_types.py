from datetime import date

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


# ── Approved floater holiday dates (2026) ───────────────────────────
# Employees may only apply Floater Leave on these specific dates.
FLOATER_DATES_2026: frozenset[date] = frozenset([
    date(2026, 1, 14),   # Pongal / Makar Sankranti
    date(2026, 1, 23),   # Vasant Panchami
    date(2026, 2, 15),   # Maha Shivratri
    date(2026, 2, 19),   # Shivaji Jayanti
    date(2026, 3, 19),   # Ugadi / Gudi Padwa
    date(2026, 3, 21),   # Ramzan Eid
    date(2026, 3, 31),   # Mahavir Jayanti
    date(2026, 4, 3),    # Good Friday
    date(2026, 4, 14),   # Ambedkar Jayanti
    date(2026, 5, 27),   # Bakrid
    date(2026, 6, 26),   # Muharram
    date(2026, 8, 15),   # Independence Day
    date(2026, 8, 26),   # Onam
    date(2026, 8, 28),   # Raksha Bandhan
    date(2026, 9, 4),    # Janmashtami
    date(2026, 10, 20),  # Dussehra
    date(2026, 11, 8),   # Diwali
    date(2026, 11, 11),  # Bhai Duj
    date(2026, 11, 24),  # Guru Nanak Jayanti
    date(2026, 12, 23),  # Hazarat Ali's Birthday
])

# Fixed public holidays (2026) — not leave, just informational
FIXED_HOLIDAYS_2026: frozenset[date] = frozenset([
    date(2026, 1, 1),    # New Year's Day
    date(2026, 1, 26),   # Republic Day
    date(2026, 3, 4),    # Holi
    date(2026, 5, 1),    # Maharashtra Day
    date(2026, 9, 14),   # Ganesh Chaturthi
    date(2026, 10, 2),   # Mahatma Gandhi Jayanti
    date(2026, 11, 9),   # Govardhan Puja
    date(2026, 12, 25),  # Christmas
])

FLOATER_DATES_BY_YEAR: dict[int, frozenset[date]] = {
    2026: FLOATER_DATES_2026,
}


def get_floater_dates_for_year(year: int) -> frozenset[date]:
    return FLOATER_DATES_BY_YEAR.get(year, frozenset())


def is_valid_floater_date(d: date) -> bool:
    return d in get_floater_dates_for_year(d.year)


def normalize_leave_type(leave_type: str) -> str:
    normalized = (leave_type or "").strip().lower().replace("-", "_").replace(" ", "_")
    return LEGACY_LEAVE_TYPE_ALIASES.get(normalized, normalized)


def get_leave_type_label(leave_type: str) -> str:
    normalized = normalize_leave_type(leave_type)
    return LEAVE_TYPE_LABELS.get(normalized, normalized.replace("_", " ").title())
