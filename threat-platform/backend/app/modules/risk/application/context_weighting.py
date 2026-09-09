"""Time-of-day and business-context adjustments.

TODO: an admin login at 03:00 on a school network is more interesting than the
same login at 10:00. Implement once you have two weeks of baseline data.
"""


def off_hours_multiplier(hour_utc: int, *, business_hours: tuple[int, int] = (8, 19)) -> float:
    start, end = business_hours
    return 1.15 if hour_utc < start or hour_utc >= end else 1.0
