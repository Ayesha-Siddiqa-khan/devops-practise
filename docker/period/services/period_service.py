from datetime import date, datetime, timedelta


def validate_cycle_input(last_period_date: str, cycle_length_raw: str):
    """Validate period tracker form inputs and return parsed values."""
    errors = []
    parsed_date = None
    cycle_length = None

    if not last_period_date:
        errors.append("Please select your last period date.")

    if not cycle_length_raw:
        errors.append("Please enter your cycle length.")

    if cycle_length_raw:
        try:
            cycle_length = int(cycle_length_raw)
            if cycle_length < 21 or cycle_length > 45:
                errors.append("Cycle length should be between 21 and 45 days.")
        except ValueError:
            errors.append("Cycle length must be a valid number.")

    if last_period_date:
        try:
            parsed_date = datetime.strptime(last_period_date, "%Y-%m-%d").date()
            if parsed_date > date.today():
                errors.append("Last period date cannot be in the future.")
        except ValueError:
            errors.append("Invalid date format. Please use the date picker.")

    return errors, parsed_date, cycle_length


def calculate_cycle_predictions(parsed_date: date, cycle_length: int):
    """Calculate period, ovulation, and fertile window information."""
    next_period = parsed_date + timedelta(days=cycle_length)
    ovulation_day = next_period - timedelta(days=14)
    fertile_start = ovulation_day - timedelta(days=5)
    fertile_end = ovulation_day + timedelta(days=1)

    # Build a simple 35-day mini calendar around the expected cycle events.
    calendar_start = parsed_date
    calendar_days = []
    for i in range(35):
        day = calendar_start + timedelta(days=i)
        marker = "normal"
        if fertile_start <= day <= fertile_end:
            marker = "fertile"
        if day == ovulation_day:
            marker = "ovulation"
        if day == next_period:
            marker = "next_period"

        calendar_days.append(
            {
                "iso": day.isoformat(),
                "label": day.strftime("%d %b"),
                "marker": marker,
            }
        )

    timeline = [
        {"title": "Last Period", "date": parsed_date.strftime("%b %d, %Y"), "tone": "base"},
        {"title": "Fertile Window Starts", "date": fertile_start.strftime("%b %d, %Y"), "tone": "info"},
        {"title": "Ovulation Day", "date": ovulation_day.strftime("%b %d, %Y"), "tone": "success"},
        {"title": "Fertile Window Ends", "date": fertile_end.strftime("%b %d, %Y"), "tone": "info"},
        {"title": "Next Period", "date": next_period.strftime("%b %d, %Y"), "tone": "accent"},
    ]

    return {
        "next_period": next_period.strftime("%B %d, %Y"),
        "ovulation_day": ovulation_day.strftime("%B %d, %Y"),
        "fertile_window": f"{fertile_start.strftime('%B %d, %Y')} to {fertile_end.strftime('%B %d, %Y')}",
        "timeline": timeline,
        "calendar_days": calendar_days,
    }
