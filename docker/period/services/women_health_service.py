PROBLEM_LIBRARY = {
    "pcos": {
        "explanation": "PCOS is a hormone-related condition that can affect periods, skin, and fertility.",
        "causes": ["Insulin resistance", "Family history", "Hormonal imbalance", "Lifestyle factors"],
        "advice": "Track periods, maintain healthy weight habits, and consult a gynecologist for hormone guidance.",
    },
    "hormonal_imbalance": {
        "explanation": "Hormonal imbalance can affect menstrual cycle, mood, skin, and energy levels.",
        "causes": ["Stress", "Thyroid issues", "PCOS", "Sleep disruption"],
        "advice": "Prioritize sleep, stress control, and discuss hormone testing with your doctor if symptoms continue.",
    },
    "irregular_periods": {
        "explanation": "Cycle timing changes can happen due to hormones, stress, or health conditions.",
        "causes": ["Stress", "Weight changes", "Hormonal imbalance", "PCOS"],
        "advice": "Track cycles for 3 months, improve sleep, and discuss persistent irregularity with a doctor.",
    },
    "heavy_bleeding": {
        "explanation": "Very heavy flow can lead to weakness and may need medical review.",
        "causes": ["Fibroids", "Hormonal issues", "Thyroid disorders", "Bleeding disorders"],
        "advice": "If soaking pads quickly or feeling dizzy, seek medical care early.",
    },
    "severe_cramps": {
        "explanation": "Severe cramps that disturb routine may need clinical evaluation.",
        "causes": ["Endometriosis", "Adenomyosis", "Pelvic inflammation", "Primary dysmenorrhea"],
        "advice": "Use heat therapy and rest. If pain limits daily activity, consult a gynecologist.",
    },
    "missed_periods": {
        "explanation": "Missed periods can occur for many reasons, including pregnancy or hormonal shifts.",
        "causes": ["Pregnancy", "Stress", "Hormonal imbalance", "Thyroid issues"],
        "advice": "Do a pregnancy test if applicable and seek evaluation if missed periods continue.",
    },
    "vaginal_infections": {
        "explanation": "Vaginal infections can cause odor, irritation, and unusual discharge.",
        "causes": ["Bacterial imbalance", "Fungal overgrowth", "Poor hygiene habits", "Antibiotic use"],
        "advice": "Avoid harsh products, keep area dry, and consult a doctor for proper treatment.",
    },
}


def analyze_women_problem(problem_key: str):
    return PROBLEM_LIBRARY.get(problem_key)
