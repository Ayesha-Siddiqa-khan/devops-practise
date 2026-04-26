def assess_pregnancy_risk(high_bp: str, bleeding: str, diabetes: str, pain_level: str):
    """Return risk level based on simple weighted conditions."""
    score = 0

    if high_bp == "yes":
        score += 2
    if bleeding == "yes":
        score += 3
    if diabetes == "yes":
        score += 2

    pain_weights = {"low": 0, "medium": 2, "high": 4}
    score += pain_weights.get(pain_level, 0)

    if score <= 2:
        return {
            "level": "Low",
            "message": "Current answers suggest low immediate risk. Continue regular checkups and healthy routine.",
            "doctor_visit": False,
        }
    if score <= 6:
        return {
            "level": "Medium",
            "message": "Some concerning signs are present. Schedule a doctor consultation soon.",
            "doctor_visit": True,
        }

    return {
        "level": "High",
        "message": "High-risk signals detected. Seek medical attention immediately.",
        "doctor_visit": True,
    }
