import random
import re


DISTRESS_PATTERNS = [
    r"\b(hopeless|no reason to live|want to die|end my life|self harm|suicide|kill myself)\b",
]

GREETING_KEYWORDS = {"hi", "hello", "hey", "hii", "hlo", "yo", "namaste", "good morning", "good evening"}

MOOD_KEYWORDS = {
    "sad": ["sad", "down", "cry", "empty", "lonely", "heartbroken", "hurt"],
    "anxious": ["anxious", "panic", "worried", "overthinking", "restless", "scared", "nervous"],
    "stressed": ["stressed", "pressure", "overwhelmed", "burnout", "tense", "exhausted"],
    "happy": ["happy", "good", "better", "calm", "grateful", "relaxed"],
}

# Modular catalog: add a new topic by appending a new key with keywords and response pools.
INTENT_CATALOG = {
    "period_problems": {
        "topic": "period",
        "keywords": [
            "period",
            "cycle",
            "cramp",
            "menstrual",
            "pms",
            "bleeding",
            "spotting",
            "irregular",
            "late period",
            "heavy flow",
        ],
        "empathy": [
            "Periods can feel physically and emotionally draining, and your feelings are valid.",
            "That sounds uncomfortable, and I am really glad you shared it.",
            "Cycle symptoms can be a lot to carry, especially when they disrupt daily life.",
        ],
        "guidance": [
            "For cramps, try warmth on the lower belly, hydration, and very light stretching for 10 to 15 minutes.",
            "Track pain level, flow, mood, and sleep for a few cycles to spot patterns you can discuss with a clinician.",
            "If bleeding is very heavy, pain is severe, or you feel dizzy or faint, seek medical care quickly.",
        ],
        "followups": [
            "Is your main issue pain, heavy bleeding, delayed cycle, or mood changes before periods?",
            "Would you like a simple 3-day comfort routine for cramps and low energy?",
            "Do you want help setting up a mood-plus-cycle tracking template?",
        ],
    },
    "stress_relief": {
        "topic": "stress",
        "keywords": ["stress", "stressed", "pressure", "overwhelmed", "burnout", "workload", "deadline", "tension"],
        "empathy": [
            "You are carrying a lot right now, and it makes sense to feel this way.",
            "That sounds very heavy, and you do not have to handle it all at once.",
            "Thank you for opening up. Stress can feel intense when it builds up.",
        ],
        "guidance": [
            "Try one quick reset: inhale for 4 seconds, exhale for 6 seconds, and repeat for one minute.",
            "Choose only one tiny next task and postpone everything else for 15 minutes.",
            "A short walk, water, and shoulder relaxation can help your body de-escalate quickly.",
        ],
        "followups": [
            "Would you like a 1-minute reset or a 10-minute evening stress plan?",
            "Is your stress mainly from work, study, home responsibilities, or relationship pressure?",
            "Do you want me to help you break one overwhelming task into small steps?",
        ],
    },
    "anxiety_support": {
        "topic": "anxiety",
        "keywords": ["anxiety", "anxious", "panic", "worried", "overthinking", "fear", "nervous", "palpitations"],
        "empathy": [
            "I hear you. Anxiety can feel scary in the moment.",
            "You are not alone in this feeling, and I am here with you.",
            "That sounds hard, especially when your mind keeps racing.",
        ],
        "guidance": [
            "Try grounding: name 5 things you see, 4 things you feel, and 3 things you hear.",
            "Take slow breaths and gently unclench your jaw and shoulders.",
            "Sip water and remind yourself: this feeling can pass, one minute at a time.",
        ],
        "followups": [
            "Do you feel this more in your thoughts, your body, or both?",
            "Would you like a short grounding exercise I can guide step by step?",
            "Are there specific triggers that usually start this anxious feeling?",
        ],
    },
    "family_social": {
        "topic": "family_social",
        "keywords": [
            "family",
            "husband",
            "partner",
            "boyfriend",
            "friend",
            "mother",
            "father",
            "in-laws",
            "argument",
            "fight",
            "relationship",
            "social",
            "alone",
            "unsupported",
        ],
        "empathy": [
            "Relationship and family stress can feel deeply personal and exhausting.",
            "I am sorry you are going through this. Social conflict can affect your whole day.",
            "Feeling unheard by people close to you can hurt a lot.",
        ],
        "guidance": [
            "When emotions are high, pause before replying and use short, calm sentences about your needs.",
            "It can help to say: 'I want to solve this, but I need a calm conversation.'",
            "Protect your energy with boundaries, rest, and at least one supportive contact if possible.",
        ],
        "followups": [
            "Do you want help drafting a calm message for this person?",
            "Is this conflict recent, or something that has been repeating for weeks?",
            "Would you like coping tips for tonight while this situation settles?",
        ],
    },
    "diet_support": {
        "topic": "diet",
        "keywords": ["diet", "food", "meal", "nutrition", "protein", "fiber", "weight", "eat", "eating", "cravings"],
        "empathy": [
            "Food choices can feel confusing, especially when mood and hormones change.",
            "You are doing the right thing by asking for a practical plan.",
            "Small food changes can create a big difference over time.",
        ],
        "guidance": [
            "Use a simple plate pattern: half vegetables, quarter protein, quarter whole grains.",
            "Add protein plus fiber to each meal to improve energy and reduce sudden cravings.",
            "Keep hydration steady, especially during periods, stress, or poor sleep days.",
        ],
        "followups": [
            "Would you like vegetarian meal ideas or mixed meal ideas?",
            "Is your goal energy balance, weight support, period comfort, or stress eating control?",
            "Should I suggest a simple one-day meal plan using common home foods?",
        ],
    },
    "mood_tracking": {
        "topic": "mood_tracking",
        "keywords": ["mood", "track", "journal", "log", "emotion", "daily check", "pattern", "feelings tracker"],
        "empathy": [
            "Mood tracking is a strong self-care step, and it can build real clarity.",
            "You are being thoughtful about your mental health, which is a big positive.",
            "Tracking emotions can help you feel more in control over time.",
        ],
        "guidance": [
            "Log mood (1-10), sleep hours, energy, stress trigger, and cycle day once daily.",
            "Keep notes brief so it stays realistic and consistent.",
            "Review weekly for patterns like low mood before periods or anxiety after poor sleep.",
        ],
        "followups": [
            "Would you like a simple 5-column tracker format you can copy today?",
            "Do you want to track once per day or morning and evening?",
            "Should we connect mood tracking with your cycle tracking too?",
        ],
    },
    "sadness_support": {
        "topic": "sadness",
        "keywords": ["sad", "down", "cry", "lonely", "empty", "hurt", "hopeless", "upset"],
        "empathy": [
            "I am really glad you shared this. You do not have to hide how you feel here.",
            "That sounds painful, and your feelings matter.",
            "I hear you. Sad days can feel heavy and slow.",
        ],
        "guidance": [
            "Try a gentle reset: slow breathing, a glass of water, and one comforting activity for 10 minutes.",
            "If possible, message one trusted person just to say you need a little support.",
            "Give yourself a smaller goal for today instead of pushing through everything.",
        ],
        "followups": [
            "What feels hardest right now, your thoughts, your energy, or something that happened today?",
            "Would you like a calming evening routine for low-mood days?",
            "Do you want to talk through what triggered this feeling?",
        ],
    },
    "general_conversation": {
        "topic": "general",
        "keywords": [],
        "empathy": [
            "I am here with you and happy to listen.",
            "Thank you for checking in. We can take this one step at a time.",
            "I am glad you reached out today.",
        ],
        "guidance": [
            "I can support mood check-ins, period issues, stress relief, diet habits, and family or social concerns.",
            "Share one area you want to improve this week, and I will suggest a simple plan.",
            "You can keep it short. Even one line is enough to begin.",
        ],
        "followups": [
            "What would help you most right now: emotional support, period comfort, stress reset, diet tips, or relationship support?",
            "How has your day felt overall: calm, stressful, low, or mixed?",
            "Would you like to start with a quick mood check-in?",
        ],
    },
}


def detect_distress(message: str) -> bool:
    text = (message or "").lower()
    return any(re.search(pattern, text) for pattern in DISTRESS_PATTERNS)


def classify_mood(message: str) -> str:
    text = (message or "").lower()
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(word in text for word in keywords):
            return mood
    return "neutral"


def is_greeting(message: str) -> bool:
    return (message or "").strip().lower() in GREETING_KEYWORDS


def _recent_assistant_messages(history: list, limit: int = 4) -> list[str]:
    lines = []
    for item in reversed(history or []):
        if item.get("role") == "assistant":
            lines.append(str(item.get("text", "")).strip())
        if len(lines) >= limit:
            break
    return lines


def _pick_non_repeating(options: list[str], recent_text: str, fallback: str) -> str:
    if not options:
        return fallback

    # Randomized ordering provides varied responses; anti-repeat avoids robotic loops.
    shuffled = options[:]
    random.shuffle(shuffled)
    for option in shuffled:
        if option and option not in recent_text:
            return option
    return shuffled[0] or fallback


def detect_intent(message: str) -> str:
    text = (message or "").lower()
    intent_scores = {}

    for intent, config in INTENT_CATALOG.items():
        keywords = config.get("keywords", [])
        if not keywords:
            continue
        score = sum(1 for keyword in keywords if keyword in text)
        if score:
            intent_scores[intent] = score

    if not intent_scores:
        return "general_conversation"
    return max(intent_scores, key=intent_scores.get)


def _previous_user_intent(history: list) -> str:
    for item in reversed(history or []):
        if item.get("role") == "user":
            return detect_intent(str(item.get("text", "")))
    return "general_conversation"


def _greeting_reply(history: list) -> str:
    recent_text = "\n".join(_recent_assistant_messages(history))
    choices = [
        "Hi, I am here with you. How are you feeling emotionally today?",
        "Hello, thank you for checking in. Would you like a quick mood check, stress support, or period-care guidance?",
        "Hey, I am glad you reached out. What feels most important right now: mood, stress, cycle symptoms, diet, or family pressure?",
    ]
    return _pick_non_repeating(choices, recent_text, "Hi, I am here with you.")


def generate_chat_reply(message: str, history: list):
    text = (message or "").strip()

    if not text:
        return {
            "reply": "How are you feeling today?\nShare a few words and I will support you gently.",
            "mood": "neutral",
            "intent": "general_conversation",
            "topic": "general",
            "urgent": False,
        }

    if detect_distress(text):
        return {
            "reply": (
                "I am really glad you told me this.\n"
                "Your safety matters right now. Please contact a trusted person immediately and seek professional crisis support.\n"
                "If you feel at immediate risk, call local emergency services now."
            ),
            "mood": "distress",
            "intent": "crisis_support",
            "topic": "safety",
            "urgent": True,
        }

    if is_greeting(text):
        return {
            "reply": _greeting_reply(history),
            "mood": "neutral",
            "intent": "general_conversation",
            "topic": "general",
            "urgent": False,
        }

    mood = classify_mood(text)
    intent = detect_intent(text)
    intent_config = INTENT_CATALOG.get(intent, INTENT_CATALOG["general_conversation"])
    topic = intent_config.get("topic", "general")

    recent_text = "\n".join(_recent_assistant_messages(history))
    previous_intent = _previous_user_intent(history)

    empathy = _pick_non_repeating(
        intent_config.get("empathy", []),
        recent_text,
        "I hear you, and I am here to support you.",
    )
    guidance = _pick_non_repeating(
        intent_config.get("guidance", []),
        recent_text,
        "Let us take one small step at a time.",
    )
    followup = _pick_non_repeating(
        intent_config.get("followups", []),
        recent_text,
        "Would you like to share a little more so I can support you better?",
    )

    # Context awareness: acknowledge continuity when the same intent appears across turns.
    continuity_line = ""
    if previous_intent == intent and intent != "general_conversation":
        continuity_line = "Thank you for sharing more about this. Let us build on what you already noticed."

    lines = [line for line in [continuity_line, empathy, guidance, followup] if line]

    if mood in {"sad", "anxious", "stressed"} and "1-minute" not in " ".join(lines):
        lines.append("If helpful, I can guide a 1-minute calming practice right now.")

    return {
        "reply": "\n".join(lines),
        "mood": mood,
        "intent": intent,
        "topic": topic,
        "urgent": False,
    }
