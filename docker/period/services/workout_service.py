from copy import deepcopy


EXERCISE_LIBRARY = {
    "warmup_walk": {
        "name": "Warm-up Walk",
        "image": "/static/images/workouts/warmup_walk.svg",
        "video_preview": "",
        "target": "5-10 minutes",
        "sets": "1 set",
        "difficulty": "Easy",
        "timer_seconds": 120,
        "safety": "all",
        "notes": "Start with gentle pace and relaxed breathing.",
        "instructions": "Keep shoulders relaxed, look forward, and breathe naturally.",
    },
    "squats": {
        "name": "Bodyweight Squats",
        "image": "/static/images/workouts/squats.svg",
        "video_preview": "",
        "target": "10-15 reps",
        "sets": "3 sets",
        "difficulty": "Medium",
        "timer_seconds": 40,
        "safety": "general",
        "notes": "Keep chest up and knees aligned with toes.",
        "instructions": "Lower hips as if sitting on a chair and push through heels to stand.",
    },
    "lunges": {
        "name": "Forward Lunges",
        "image": "/static/images/workouts/lunges.svg",
        "video_preview": "",
        "target": "10 reps each leg",
        "sets": "2 sets",
        "difficulty": "Medium",
        "timer_seconds": 40,
        "safety": "general",
        "notes": "Step forward slowly and keep balance stable.",
        "instructions": "Bend both knees to about 90 degrees and keep front knee above ankle.",
    },
    "plank": {
        "name": "Plank Hold",
        "image": "/static/images/workouts/plank.svg",
        "video_preview": "",
        "target": "20-60 seconds",
        "sets": "3 sets",
        "difficulty": "Medium",
        "timer_seconds": 30,
        "safety": "general",
        "notes": "Keep core engaged and avoid lower-back strain.",
        "instructions": "Maintain a straight line from shoulders to heels with engaged core.",
    },
    "brisk_walk": {
        "name": "Walking / Light Jogging",
        "image": "/static/images/workouts/brisk_walk.svg",
        "video_preview": "",
        "target": "1000-5000 steps (or 5-10 laps)",
        "sets": "1 session",
        "difficulty": "Easy",
        "timer_seconds": 180,
        "safety": "all",
        "notes": "Maintain comfortable pace and hydrate well.",
        "instructions": "Keep a steady rhythm and swing arms naturally.",
    },
    "stretching": {
        "name": "Full Body Stretching",
        "image": "/static/images/workouts/stretching.svg",
        "video_preview": "",
        "target": "5-10 minutes",
        "sets": "1 session",
        "difficulty": "Easy",
        "timer_seconds": 90,
        "safety": "all",
        "notes": "Move gently and avoid painful ranges.",
        "instructions": "Hold each stretch for 15-20 seconds without bouncing.",
    },
    "prenatal_yoga": {
        "name": "Prenatal Yoga",
        "image": "/static/images/workouts/prenatal_yoga.svg",
        "video_preview": "",
        "target": "10-20 minutes",
        "sets": "1 session",
        "difficulty": "Easy",
        "timer_seconds": 120,
        "safety": "pregnancy",
        "notes": "Use pregnancy-safe poses and avoid lying flat too long.",
        "instructions": "Focus on breathing and slow controlled poses recommended in prenatal classes.",
    },
    "breathing": {
        "name": "Breathing Exercise",
        "image": "/static/images/workouts/breathing.svg",
        "video_preview": "",
        "target": "5 minutes",
        "sets": "1 session",
        "difficulty": "Easy",
        "timer_seconds": 120,
        "safety": "all",
        "notes": "Inhale slowly for 4 counts and exhale for 6 counts.",
        "instructions": "Sit comfortably, place one hand on chest and one on abdomen, then breathe slowly.",
    },
    "mountain_climbers": {
        "name": "Mountain Climbers",
        "image": "/static/images/workouts/plank.svg",
        "video_preview": "",
        "target": "20-30 reps",
        "sets": "3 sets",
        "difficulty": "Hard",
        "timer_seconds": 35,
        "safety": "advanced",
        "notes": "Keep pace controlled and core stable.",
        "instructions": "Start in plank and drive knees toward chest one at a time quickly.",
    },
    "glute_bridge": {
        "name": "Glute Bridges",
        "image": "/static/images/workouts/stretching.svg",
        "video_preview": "",
        "target": "12-15 reps",
        "sets": "3 sets",
        "difficulty": "Easy",
        "timer_seconds": 45,
        "safety": "general",
        "notes": "Press heels down and squeeze glutes at the top.",
        "instructions": "Lift hips slowly, pause briefly, and lower down with control.",
    },
}


def _to_exercise_card(item_key: str):
    base = deepcopy(EXERCISE_LIBRARY[item_key])
    base["key"] = item_key
    return base


def _remove_keys(keys: list[str], removable: set[str]):
    return [key for key in keys if key not in removable]


def _apply_cycle_adjustments(day1_keys: list[str], day2_keys: list[str], cycle_phase: str, is_pregnancy_mode: bool):
    if is_pregnancy_mode:
        return day1_keys, day2_keys, "Pregnancy-safe intensity is active."

    if cycle_phase == "period":
        # Keep intensity gentle during periods.
        low_intensity_remove = {"mountain_climbers", "plank", "lunges"}
        day1_keys = _remove_keys(day1_keys, low_intensity_remove)
        day2_keys = _remove_keys(day2_keys, low_intensity_remove)
        if "stretching" not in day1_keys:
            day1_keys.append("stretching")
        if "breathing" not in day2_keys:
            day2_keys.append("breathing")
        return day1_keys, day2_keys, "Cycle phase adjustment: low intensity mode for period comfort."

    if cycle_phase == "ovulation":
        # Energy may feel higher for many users in ovulation window.
        if "mountain_climbers" not in day1_keys:
            day1_keys.append("mountain_climbers")
        if "plank" not in day2_keys:
            day2_keys.append("plank")
        return day1_keys, day2_keys, "Cycle phase adjustment: higher-intensity mode for ovulation window."

    return day1_keys, day2_keys, "Cycle phase adjustment: balanced intensity mode."


def generate_daily_workout_plan(
    age: int,
    fitness_level: str,
    goal: str,
    activity_level: str,
    cycle_phase: str,
    thyroid: str,
    pcos: str,
    pregnancy: str,
):
    """Generate a safe, beginner-friendly daily workout plan."""
    is_pregnancy_mode = pregnancy == "yes" or goal == "pregnancy_safe"

    if is_pregnancy_mode:
        day1_keys = ["warmup_walk", "prenatal_yoga", "breathing", "stretching"]
        day2_keys = ["brisk_walk", "breathing", "stretching", "prenatal_yoga"]
        safety_warning = "Always consult a doctor before exercising during pregnancy."
    else:
        if fitness_level == "beginner" or age >= 38:
            day1_keys = ["warmup_walk", "squats", "lunges", "stretching"]
            day2_keys = ["brisk_walk", "plank", "breathing", "stretching"]
        elif fitness_level == "intermediate":
            day1_keys = ["warmup_walk", "squats", "lunges", "plank", "stretching"]
            day2_keys = ["brisk_walk", "squats", "plank", "breathing", "stretching"]
        else:
            day1_keys = ["warmup_walk", "squats", "lunges", "plank", "brisk_walk", "stretching"]
            day2_keys = ["brisk_walk", "squats", "lunges", "plank", "breathing", "stretching"]

        safety_warning = "Hydrate well, rest between sets, and stop if pain or dizziness occurs."

    if activity_level == "low" and "stretching" not in day2_keys:
        day2_keys.append("stretching")
    if activity_level == "high" and not is_pregnancy_mode and "plank" not in day1_keys:
        day1_keys.append("plank")

    if goal == "weight_gain" and not is_pregnancy_mode and "glute_bridge" not in day1_keys:
        day1_keys.append("glute_bridge")
    if goal == "weight_loss" and not is_pregnancy_mode and "brisk_walk" not in day2_keys:
        day2_keys.insert(0, "brisk_walk")

    if thyroid == "yes":
        day2_keys.insert(0, "breathing")
    if pcos == "yes" and "brisk_walk" not in day1_keys:
        day1_keys.insert(1, "brisk_walk")

    day1_keys, day2_keys, cycle_note = _apply_cycle_adjustments(day1_keys, day2_keys, cycle_phase, is_pregnancy_mode)

    # Preserve order but remove duplicates from inserts.
    day1_keys = list(dict.fromkeys(day1_keys))
    day2_keys = list(dict.fromkeys(day2_keys))

    day1 = [_to_exercise_card(key) for key in day1_keys]
    day2 = [_to_exercise_card(key) for key in day2_keys]

    return {
        "day1": day1,
        "day2": day2,
        "all_exercises": day1 + day2,
        "is_pregnancy_mode": is_pregnancy_mode,
        "safety_warning": safety_warning,
        "cycle_phase": cycle_phase,
        "cycle_note": cycle_note,
        "hydration_note": "Drink water before, during, and after workouts.",
        "rest_note": "Keep at least 1 rest day between intense sessions.",
    }
