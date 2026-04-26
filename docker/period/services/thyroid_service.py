def assess_thyroid_awareness(
    weight_change: str,
    fatigue: str,
    hair_fall: str,
    temp_sensitivity: str,
    irregular_periods: str,
):
    """Educational thyroid-awareness scorer. Non-diagnostic by design."""
    score = 0

    if weight_change in {"gain", "loss"}:
        score += 2
    if fatigue == "yes":
        score += 2
    if hair_fall == "yes":
        score += 1
    if temp_sensitivity in {"cold", "heat"}:
        score += 1
    if irregular_periods == "yes":
        score += 2

    if score <= 2:
        return {
            "risk": "Low",
            "status": "normal",
            "icon": "🟢",
            "explanation": "Current answers show low thyroid warning burden.",
            "possible_pattern": "No clear imbalance pattern from selected inputs.",
            "advice": "Continue healthy routine and regular health checkups.",
        }

    if score <= 5:
        possible_pattern = "Possible mild thyroid imbalance pattern"
        if temp_sensitivity == "cold" and weight_change == "gain":
            possible_pattern = "Possible hypothyroid-like pattern (low thyroid activity signs)"
        elif temp_sensitivity == "heat" and weight_change == "loss":
            possible_pattern = "Possible hyperthyroid-like pattern (high thyroid activity signs)"

        return {
            "risk": "Medium",
            "status": "monitor",
            "icon": "🟡",
            "explanation": "Some thyroid-related warning signs are present.",
            "possible_pattern": possible_pattern,
            "advice": "Consider discussing TSH, T3, and T4 testing with your doctor.",
        }

    return {
        "risk": "High",
        "status": "emergency",
        "icon": "🔴",
        "explanation": "Multiple thyroid-related warning signs are present.",
        "possible_pattern": "Possible thyroid imbalance needs professional assessment.",
        "advice": "Please consult a doctor soon and ask about TSH, T3, and T4 tests.",
    }
