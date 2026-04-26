def evaluate_leucorrhea(color: str, smell: str, itching: str):
    """Classify discharge pattern as likely normal or possibly infectious."""
    normal_colors = {"clear", "white"}
    concerning_colors = {"yellow", "green", "gray"}

    likely_infection = False

    if color in concerning_colors:
        likely_infection = True
    if smell in {"foul", "fishy"}:
        likely_infection = True
    if itching == "yes":
        likely_infection = True

    if likely_infection:
        return {
            "status": "Possible infection",
            "explanation": "Your answers may indicate vaginal infection or imbalance. A medical check can confirm the cause.",
            "tips": [
                "Use breathable cotton underwear",
                "Avoid scented soaps and sprays",
                "Keep intimate area dry",
                "Consult a gynecologist for testing",
            ],
        }

    return {
        "status": "Likely normal",
        "explanation": "Your current answers look similar to common physiological discharge patterns.",
        "tips": [
            "Maintain daily gentle hygiene",
            "Stay hydrated",
            "Avoid harsh products",
            "Observe changes and seek care if symptoms appear",
        ],
    }
