def assess_labor_emergency(
    water_broken: str,
    fluid_color: str,
    bad_smell: str,
    fever: str,
    baby_movement: str,
):
    """Assess labor and water-break safety flags with supportive messaging."""
    cards = []
    labor_stage_guidance = None
    emergency_reasons = []
    warning_reasons = []

    if water_broken == "yes":
        cards.append(
            {
                "level": "monitor",
                "icon": "⚠️",
                "title": "Water break reported",
                "message": "Stay calm, note the exact time, avoid inserting anything vaginally, and go to the hospital for evaluation.",
            }
        )
        labor_stage_guidance = {
            "heading": "You may be entering labor",
            "contractions": "Contractions often feel like tightening waves that become stronger, longer, and closer together.",
            "advice": "Remain at or proceed to the hospital so a medical team can monitor you and your baby safely.",
        }

    if fluid_color in {"green", "brown"}:
        emergency_reasons.append("Fluid color may indicate possible baby distress")

    if bad_smell == "yes" or fever == "yes":
        warning_reasons.append("Infection warning signs may be present")

    if baby_movement in {"reduced", "none"}:
        emergency_reasons.append("Baby movement is reduced or absent")

    for reason in emergency_reasons:
        cards.append(
            {
                "level": "emergency",
                "icon": "🚨",
                "title": "Emergency action needed",
                "message": f"{reason}. Please go to the nearest hospital immediately.",
            }
        )

    for reason in warning_reasons:
        cards.append(
            {
                "level": "monitor",
                "icon": "⚠️",
                "title": "Medical warning",
                "message": f"{reason}. Contact your doctor or maternity triage urgently.",
            }
        )

    if not cards:
        cards.append(
            {
                "level": "normal",
                "icon": "✅",
                "title": "No immediate danger signs from selected inputs",
                "message": "Continue monitoring symptoms calmly. If anything worsens, contact your doctor promptly.",
            }
        )

    level_rank = {"normal": 1, "monitor": 2, "emergency": 3}
    overall = max(cards, key=lambda item: level_rank[item["level"]])["level"]

    return {
        "overall": overall,
        "cards": cards,
        "labor_stage_guidance": labor_stage_guidance,
    }


def assess_postpartum_warning(postpartum_flags: dict):
    """Check postpartum warning signs and return safety guidance."""
    normal_conditions = [
        "Light bleeding can continue for a few weeks",
        "Temporary weakness is common",
        "Mood shifts may happen during recovery",
        "Breastfeeding adjustment takes time",
    ]

    warning_map = {
        "heavy_bleeding": "Heavy bleeding with pads soaking quickly",
        "high_fever": "High fever",
        "severe_abdominal_pain": "Severe abdominal pain",
        "foul_discharge": "Foul-smelling discharge",
        "extreme_sadness": "Extreme sadness or depression symptoms",
    }

    triggered = [
        warning_label
        for key, warning_label in warning_map.items()
        if postpartum_flags.get(key, "no") == "yes"
    ]

    if triggered:
        return {
            "level": "emergency",
            "icon": "🚨",
            "message": "Consult doctor immediately. In severe symptoms, go to the nearest hospital immediately.",
            "triggered": triggered,
            "normal_conditions": normal_conditions,
        }

    return {
        "level": "normal",
        "icon": "✅",
        "message": "No selected warning signs right now. Continue postpartum follow-up and rest.",
        "triggered": [],
        "normal_conditions": normal_conditions,
    }


def smart_emergency_response(text: str):
    """Keyword-based smart response for labor and postpartum emergencies."""
    normalized = (text or "").lower().strip()

    if not normalized:
        return {
            "level": "monitor",
            "icon": "⚠️",
            "title": "Please enter your message",
            "response": "Type your symptom or concern, and the app will provide a safety-focused guidance response.",
        }

    water_break_keywords = ["water broke", "my water broke", "water breaking"]
    postpartum_bleeding_keywords = ["heavy bleeding after delivery", "postpartum bleeding", "heavy bleeding after birth"]

    if any(phrase in normalized for phrase in water_break_keywords):
        return {
            "level": "emergency",
            "icon": "🚨",
            "title": "Possible labor emergency response",
            "response": "Stay calm. Note the exact time your water broke, keep clean sanitary protection, and go to the hospital immediately for assessment.",
        }

    if any(phrase in normalized for phrase in postpartum_bleeding_keywords):
        return {
            "level": "emergency",
            "icon": "🚨",
            "title": "Postpartum bleeding emergency response",
            "response": "Heavy bleeding after delivery can be serious. Seek immediate hospital care now.",
        }

    if "i feel hopeless" in normalized or "no interest in life" in normalized or "no reason to live" in normalized:
        return {
            "level": "emergency",
            "icon": "🚨",
            "title": "Mental health emergency response",
            "response": "Please seek professional help immediately. If you feel unsafe, contact emergency services or go to the nearest hospital now.",
        }

    if "fever" in normalized and "postpartum" in normalized:
        return {
            "level": "monitor",
            "icon": "⚠️",
            "title": "Postpartum warning response",
            "response": "Postpartum fever can indicate infection. Contact your doctor urgently and get evaluated.",
        }

    return {
        "level": "normal",
        "icon": "✅",
        "title": "Supportive general guidance",
        "response": "Keep tracking your symptoms and contact a qualified doctor if symptoms persist or worsen.",
    }
