PREGNANCY_MONTH_DATA = {
    1: {
        "baby_development": "Embryo starts forming vital organs and neural tube.",
        "mother_changes": "Hormonal changes begin and body starts adapting.",
        "symptoms": ["Nausea", "Fatigue", "Breast tenderness"],
        "diet_tips": ["Start folic acid", "Hydrate regularly", "Eat small frequent meals"],
        "precautions": ["Avoid alcohol and smoking", "Begin prenatal checkup", "Take adequate rest"],
    },
    2: {
        "baby_development": "Facial features begin and heartbeat gets stronger.",
        "mother_changes": "Energy may improve but morning sickness can continue.",
        "symptoms": ["Food aversions", "Mood changes", "Mild bloating"],
        "diet_tips": ["Add protein-rich foods", "Include citrus fruits", "Continue prenatal vitamins"],
        "precautions": ["Avoid raw foods", "Limit caffeine", "Follow doctor supplements"],
    },
    3: {
        "baby_development": "Arms, legs, and fingers are now clearly developing.",
        "mother_changes": "Uterus grows and clothes may start feeling tight.",
        "symptoms": ["Heartburn", "Constipation", "Mild dizziness"],
        "diet_tips": ["Fiber-rich meals", "Calcium intake", "Keep hydration steady"],
        "precautions": ["Do light stretching", "Avoid overexertion", "Do routine scans"],
    },
    4: {
        "baby_development": "Baby movements may begin and bones strengthen.",
        "mother_changes": "Second trimester glow and appetite often increase.",
        "symptoms": ["Increased appetite", "Backache", "Skin changes"],
        "diet_tips": ["Balanced carbs", "Iron-rich foods", "Healthy snacks"],
        "precautions": ["Track weight gain", "Maintain posture", "Wear comfortable footwear"],
    },
    5: {
        "baby_development": "Hearing develops and baby responds to sound.",
        "mother_changes": "Visible belly growth and stronger fetal movements.",
        "symptoms": ["Leg cramps", "Nasal congestion", "Mild swelling"],
        "diet_tips": ["Magnesium foods", "Lean proteins", "Low-salt diet"],
        "precautions": ["Sleep on your side", "Use support pillow", "Report unusual swelling"],
    },
    6: {
        "baby_development": "Lungs continue maturing and sleep cycles begin.",
        "mother_changes": "Body feels heavier and lower back strain increases.",
        "symptoms": ["Back pain", "Frequent urination", "Acidity"],
        "diet_tips": ["Smaller meals", "Omega-3 intake", "More fluids"],
        "precautions": ["Avoid long standing", "Practice pelvic floor exercises", "Attend antenatal classes"],
    },
    7: {
        "baby_development": "Baby gains fat rapidly and brain growth accelerates.",
        "mother_changes": "Third trimester starts with higher fatigue.",
        "symptoms": ["Breathlessness", "Sleep issues", "Braxton Hicks contractions"],
        "diet_tips": ["High-protein meals", "Complex carbs", "Iron and calcium rich foods"],
        "precautions": ["Monitor fetal kicks", "Prepare birth plan", "Avoid stress"],
    },
    8: {
        "baby_development": "Most organs are mature; baby continues weight gain.",
        "mother_changes": "Pelvic pressure and discomfort become more frequent.",
        "symptoms": ["Pelvic pressure", "Swollen ankles", "Tiredness"],
        "diet_tips": ["Potassium-rich foods", "Hydrating fruits", "Keep meals light"],
        "precautions": ["Keep hospital bag ready", "Watch blood pressure", "Seek care for persistent pain"],
    },
    9: {
        "baby_development": "Baby reaches full term and prepares for birth.",
        "mother_changes": "Cervix starts preparing for labor.",
        "symptoms": ["Pressure", "Contractions", "Sleep difficulty"],
        "diet_tips": ["Simple nutritious meals", "Hydration", "Date fruits if advised by doctor"],
        "precautions": ["Hospital readiness", "Track contraction timing", "Keep emergency contacts handy"],
    },
}


def get_pregnancy_month_details(month: int):
    return PREGNANCY_MONTH_DATA.get(month)
