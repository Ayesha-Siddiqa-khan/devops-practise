KEYWORD_ENGINE = {
    "possible_pregnancy_issue": {
        "keywords": ["bleeding", "severe pain", "high fever", "blurred vision"],
        "suggestions": "These symptoms can be serious during pregnancy. Contact a doctor immediately.",
        "emergency": True,
    },
    "urinary_infection": {
        "keywords": ["burning urine", "frequent urination", "pelvic pain", "foul smell"],
        "suggestions": "May indicate urinary or vaginal infection. Increase water intake and get a urine test.",
        "emergency": False,
    },
    "pcos_pattern": {
        "keywords": ["acne", "weight gain", "irregular cycles", "facial hair"],
        "suggestions": "Could be related to hormonal imbalance such as PCOS. Consider hormonal evaluation.",
        "emergency": False,
    },
    "pms_pattern": {
        "keywords": ["bloating", "mood swings", "cramps", "headache"],
        "suggestions": "Likely premenstrual symptoms. Track pattern and improve sleep, hydration, and diet.",
        "emergency": False,
    },
    "breast_warning_pattern": {
        "keywords": ["breast lump", "nipple discharge", "breast skin changes", "dimpling"],
        "suggestions": "Breast-related warning signs should be medically reviewed early. Please consult a doctor.",
        "emergency": False,
    },
    "mental_crisis_pattern": {
        "keywords": ["hopeless", "no interest in life", "no reason to live", "extreme sadness", "can not go on"],
        "suggestions": "These emotional symptoms can be serious. Seek professional help immediately and contact emergency services if unsafe.",
        "emergency": True,
    },
}


def analyze_free_text_symptoms(text: str):
    normalized_text = (text or "").lower().strip()
    if not normalized_text:
        return {
            "issue": "No input",
            "suggestion": "Please enter your symptoms to get smart guidance.",
            "emergency": False,
        }

    best_match = None
    best_score = 0

    for issue_name, issue_data in KEYWORD_ENGINE.items():
        score = sum(1 for word in issue_data["keywords"] if word in normalized_text)
        if score > best_score:
            best_match = (issue_name, issue_data)
            best_score = score

    if not best_match:
        return {
            "issue": "General wellness concern",
            "suggestion": "Symptoms are unclear. Keep tracking and seek clinical advice if symptoms worsen.",
            "emergency": False,
        }

    issue_key, issue_data = best_match
    return {
        "issue": issue_key.replace("_", " ").title(),
        "suggestion": issue_data["suggestions"],
        "emergency": issue_data["emergency"],
    }
