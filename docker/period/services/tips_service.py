from datetime import date


def get_cycle_based_tip(cycle_day: int):
    if cycle_day <= 5:
        return "Period phase: prioritize hydration, iron-rich meals, and gentle movement."
    if cycle_day <= 13:
        return "Follicular phase: energy may improve, so include balanced workouts and protein-rich meals."
    if cycle_day <= 16:
        return "Ovulation window: stay hydrated and monitor body signs like cervical mucus changes."
    return "Luteal phase: reduce excess caffeine, add magnesium-rich foods, and improve sleep quality."


def get_pregnancy_tip(month: int):
    if month <= 3:
        return "First trimester: folic acid, hydration, and regular prenatal visits are key."
    if month <= 6:
        return "Second trimester: focus on iron, calcium, and moderate activity."
    return "Third trimester: monitor movement, prepare for delivery, and keep emergency contacts ready."


def get_general_hygiene_tips():
    return [
        "Use breathable cotton undergarments.",
        "Avoid self-medication for persistent symptoms.",
        "Maintain menstrual hygiene and change products regularly.",
        "Drink enough water and include fresh foods daily.",
    ]


def generate_daily_smart_tips(cycle_day_raw: str, pregnancy_month_raw: str):
    tips = []
    today = date.today().strftime("%B %d, %Y")

    if cycle_day_raw:
        try:
            cycle_day = int(cycle_day_raw)
            if 1 <= cycle_day <= 35:
                tips.append(get_cycle_based_tip(cycle_day))
        except ValueError:
            pass

    if pregnancy_month_raw:
        try:
            month = int(pregnancy_month_raw)
            if 1 <= month <= 9:
                tips.append(get_pregnancy_tip(month))
        except ValueError:
            pass

    tips.extend(get_general_hygiene_tips())

    return {"date": today, "tips": tips}
