def assess_breast_health(
    lump: str,
    pain: str,
    discharge: str,
    skin_changes: str,
):
    """Return a supportive risk summary for breast health concerns."""
    flags = {
        "lump": lump == "yes",
        "pain": pain == "yes",
        "discharge": discharge == "yes",
        "skin_changes": skin_changes == "yes",
    }
    symptom_count = sum(flags.values())

    if symptom_count == 0:
        return {
            "risk": "Low",
            "status": "normal",
            "icon": "🟢",
            "explanation": "No selected warning symptoms right now. Continue routine self-check awareness.",
            "advice": "If any new symptom appears or persists, please consult a doctor.",
        }

    if flags["lump"] or flags["discharge"]:
        base_risk = "Medium"
        status = "monitor"
        icon = "🟡"
        explanation = "A lump or nipple discharge can need medical review, even when pain is mild."
    else:
        base_risk = "Low"
        status = "monitor"
        icon = "🟡"
        explanation = "Some mild breast symptoms are present and should be monitored closely."

    if symptom_count >= 2 and (flags["lump"] or flags["discharge"]):
        return {
            "risk": "High",
            "status": "emergency",
            "icon": "🔴",
            "explanation": "Multiple warning signs are present with lump or discharge. Prompt clinical assessment is important.",
            "advice": "Please consult a doctor as soon as possible, especially if symptoms persist or worsen.",
        }

    if symptom_count >= 3:
        return {
            "risk": "High",
            "status": "emergency",
            "icon": "🔴",
            "explanation": "Multiple breast-related symptoms are selected and need urgent medical review.",
            "advice": "Please consult a doctor as soon as possible, especially if symptoms persist or worsen.",
        }

    return {
        "risk": base_risk,
        "status": status,
        "icon": icon,
        "explanation": explanation,
        "advice": "Please consult a doctor if symptoms persist.",
    }


def get_breast_self_exam_steps():
    """Return beginner-friendly self-examination guide steps."""
    return [
        {
            "icon": "fa-regular fa-eye",
            "title": "Mirror check",
            "description": "Stand in front of a mirror with arms at side, then raised. Look for visible shape or skin changes.",
        },
        {
            "icon": "fa-regular fa-hand",
            "title": "Physical touch check",
            "description": "Using finger pads in circular motion, gently feel each breast for unusual lumps or thick areas.",
        },
        {
            "icon": "fa-solid fa-arrows-up-down-left-right",
            "title": "Underarm check",
            "description": "Feel under both arms for any lump, swelling, or tenderness and note changes.",
        },
    ]


def assess_mental_wellness(
    mood: str,
    sleep_issues: str,
    stress_level: str,
    daily_interest: str,
):
    """Assess emotional status using non-diagnostic, supportive logic."""
    high_pattern = mood == "sad" and stress_level == "high" and daily_interest == "low"
    warning_keywords = mood in {"sad", "anxious"} or sleep_issues == "yes" or stress_level == "high"

    if high_pattern:
        return {
            "level": "emergency",
            "icon": "🔴",
            "title": "High emotional stress alert",
            "message": "You may be going through significant emotional strain. Please contact a mental health professional soon.",
            "tips": [
                "Reach out to a trusted person today",
                "Do not stay alone with overwhelming thoughts",
                "Seek professional support immediately",
            ],
        }

    if warning_keywords or daily_interest == "low":
        return {
            "level": "monitor",
            "icon": "🟡",
            "title": "Emotional support recommended",
            "message": "Some stress-related signs are present. Gentle self-care and early support can help.",
            "tips": [
                "Take short rest breaks and deep breathing sessions",
                "Talk to someone you trust",
                "Use simple relaxation routines before sleep",
            ],
        }

    return {
        "level": "normal",
        "icon": "🟢",
        "title": "Stable emotional status",
        "message": "No major emotional warning signs are selected right now.",
        "tips": [
            "Maintain healthy sleep habits",
            "Continue regular light activity",
            "Stay connected with supportive people",
        ],
    }


def check_mental_emergency_text(text: str):
    """Detect urgent mental health language for immediate support guidance."""
    normalized = (text or "").lower().strip()
    emergency_phrases = ["i feel hopeless", "no interest in life", "no reason to live"]

    if any(phrase in normalized for phrase in emergency_phrases):
        return {
            "triggered": True,
            "level": "emergency",
            "icon": "🔴",
            "message": "Please seek professional help immediately. If you feel unsafe, go to the nearest emergency service now.",
        }

    return {
        "triggered": False,
        "level": "normal",
        "icon": "🟢",
        "message": "No urgent mental-health crisis phrase detected in your input.",
    }
