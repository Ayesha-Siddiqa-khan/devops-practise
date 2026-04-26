const forms = document.querySelectorAll(".validated-form");
const loader = document.getElementById("global-loader");

for (const form of forms) {
  form.addEventListener("submit", (event) => {
    const requiredFields = form.querySelectorAll("[required]");
    const errors = [];

    for (const field of requiredFields) {
      const value = field.value.trim();
      if (!value) {
        const label = field.getAttribute("name") || "field";
        errors.push(`Please fill ${label.replaceAll("_", " ")}.`);
      }
    }

    const cycleLengthField = form.querySelector("#cycle_length");
    if (cycleLengthField && cycleLengthField.value) {
      const cycleValue = Number(cycleLengthField.value);
      if (!Number.isInteger(cycleValue) || cycleValue < 21 || cycleValue > 45) {
        errors.push("Cycle length should be between 21 and 45.");
      }
    }

    const cycleDayField = form.querySelector("#cycle_day");
    if (cycleDayField && cycleDayField.value) {
      const cycleDayValue = Number(cycleDayField.value);
      if (!Number.isInteger(cycleDayValue) || cycleDayValue < 1 || cycleDayValue > 35) {
        errors.push("Cycle day should be between 1 and 35.");
      }
    }

    const monthField = form.querySelector("#pregnancy_month");
    if (monthField && monthField.value) {
      const monthValue = Number(monthField.value);
      if (!Number.isInteger(monthValue) || monthValue < 1 || monthValue > 9) {
        errors.push("Pregnancy month should be between 1 and 9.");
      }
    }

    const ageField = form.querySelector("#age");
    if (ageField && ageField.value) {
      const age = Number(ageField.value);
      if (!Number.isInteger(age) || age < 13 || age > 60) {
        errors.push("Age should be between 13 and 60.");
      }
    }

    const workoutAgeField = form.querySelector("#workout_age");
    if (workoutAgeField && workoutAgeField.value) {
      const workoutAge = Number(workoutAgeField.value);
      if (!Number.isInteger(workoutAge) || workoutAge < 13 || workoutAge > 60) {
        errors.push("Age should be between 13 and 60.");
      }
    }

    const heightField = form.querySelector("#height_cm");
    if (heightField && heightField.value) {
      const height = Number(heightField.value);
      if (!Number.isFinite(height) || height < 120 || height > 210) {
        errors.push("Height should be between 120 cm and 210 cm.");
      }
    }

    const weightField = form.querySelector("#weight_kg");
    if (weightField && weightField.value) {
      const weight = Number(weightField.value);
      if (!Number.isFinite(weight) || weight < 30 || weight > 180) {
        errors.push("Weight should be between 30 kg and 180 kg.");
      }
    }

    if (errors.length > 0) {
      event.preventDefault();
      alert(errors.join("\n"));
      return;
    }

    if (loader) {
      loader.classList.remove("hidden");
      loader.classList.add("flex");
      setTimeout(() => {
        loader.classList.add("hidden");
        loader.classList.remove("flex");
      }, 700);
    }
  });
}

const laborForm = document.getElementById("labor-form");
const laborPreview = document.getElementById("labor-preview");

function setLaborPreview(level, title, message) {
  if (!laborPreview) {
    return;
  }

  laborPreview.classList.remove("status-normal", "status-monitor", "status-emergency");
  laborPreview.classList.add(`status-${level}`);
  laborPreview.innerHTML = `<p class="status-title">${title}</p><p class="text-sm mt-2">${message}</p>`;
}

function updateLaborPreview() {
  if (!laborForm || !laborPreview) {
    return;
  }

  const waterBroken = laborForm.querySelector("#water_broken")?.value || "no";
  const fluidColor = laborForm.querySelector("#fluid_color")?.value || "clear";
  const badSmell = laborForm.querySelector("#bad_smell")?.value || "no";
  const fever = laborForm.querySelector("#fever")?.value || "no";
  const babyMovement = laborForm.querySelector("#baby_movement")?.value || "normal";

  if (fluidColor === "green" || fluidColor === "brown" || babyMovement === "none") {
    setLaborPreview(
      "emergency",
      "🚨 Emergency Preview",
      "Possible baby distress signs detected. Please go to the nearest hospital immediately."
    );
    return;
  }

  if (babyMovement === "reduced" || fever === "yes" || badSmell === "yes" || waterBroken === "yes") {
    setLaborPreview(
      "monitor",
      "⚠️ Warning Preview",
      "Please stay calm, note symptom timing, and contact hospital triage promptly."
    );
    return;
  }

  setLaborPreview(
    "normal",
    "✅ Normal Preview",
    "No major warning signs selected right now. Continue monitoring and seek care if symptoms change."
  );
}

if (laborForm && laborPreview) {
  laborForm.addEventListener("change", updateLaborPreview);
  updateLaborPreview();
}

const workoutCards = [...document.querySelectorAll(".workout-card")];
const workoutSession = document.getElementById("workout-session");
const completedCountEl = document.getElementById("workout-completed-count");
const totalCountEl = document.getElementById("workout-total-count");
const progressBarEl = document.getElementById("workout-progress-bar");
const streakEl = document.getElementById("workout-streak");
const timerPanel = document.getElementById("timer-panel");
const timerDisplay = document.getElementById("timer-display");
const timerExerciseTitle = document.getElementById("timer-exercise-title");
const timerStopBtn = document.getElementById("timer-stop-btn");
const timerNextBtn = document.getElementById("timer-next-btn");

let workoutTimerInterval = null;
let activeCardIndex = -1;
let secondsLeft = 0;
const completedSet = new Set();
const workoutPlanId = workoutSession?.dataset?.planId || "";

try {
  const initialCompleted = JSON.parse(workoutSession?.dataset?.completedKeys || "[]");
  for (const item of initialCompleted) {
    completedSet.add(item);
  }
} catch (_error) {
  // Ignore invalid payload and continue with empty set.
}

function updateWorkoutProgress() {
  if (!completedCountEl || !totalCountEl || !progressBarEl) {
    return;
  }

  const completed = completedSet.size;
  const total = Number(totalCountEl.textContent) || workoutCards.length || 1;
  const percent = Math.round((completed / total) * 100);
  completedCountEl.textContent = String(completed);
  progressBarEl.style.width = `${percent}%`;
}

function formatSeconds(seconds) {
  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

function stopWorkoutTimer() {
  if (workoutTimerInterval) {
    clearInterval(workoutTimerInterval);
    workoutTimerInterval = null;
  }
}

async function markCardComplete(card, showAlert = false) {
  if (!card) {
    return;
  }
  const key = card.dataset.exerciseKey || card.dataset.exerciseName;

  if (workoutPlanId) {
    try {
      const response = await fetch("/api/workout/progress", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ plan_id: Number(workoutPlanId), exercise_key: key }),
      });
      if (response.ok) {
        const payload = await response.json();
        completedSet.clear();
        for (const completedKey of payload.completed_keys || []) {
          completedSet.add(completedKey);
        }
        if (streakEl && Number.isFinite(payload.streak_count)) {
          streakEl.textContent = String(payload.streak_count);
        }
      }
    } catch (_error) {
      // Keep local fallback if API fails.
      completedSet.add(key);
    }
  } else {
    completedSet.add(key);
  }

  completedSet.add(key);
  card.classList.add("done");
  updateWorkoutProgress();
  if (showAlert) {
    alert(`${card.dataset.exerciseName} completed. Great work!`);
  }
}

function startTimerForCard(index) {
  const card = workoutCards[index];
  if (!card) {
    return;
  }

  activeCardIndex = index;
  secondsLeft = Number(card.dataset.duration || "30");
  if (timerPanel) {
    timerPanel.classList.remove("hidden");
  }
  if (timerExerciseTitle) {
    timerExerciseTitle.textContent = card.dataset.exerciseName || "Exercise";
  }
  if (timerDisplay) {
    timerDisplay.textContent = formatSeconds(secondsLeft);
  }

  stopWorkoutTimer();
  workoutTimerInterval = setInterval(() => {
    secondsLeft -= 1;
    if (timerDisplay) {
      timerDisplay.textContent = formatSeconds(Math.max(0, secondsLeft));
    }

    if (secondsLeft <= 0) {
      stopWorkoutTimer();
      markCardComplete(card, true);

      const nextIndex = index + 1;
      if (nextIndex < workoutCards.length) {
        startTimerForCard(nextIndex);
      }
    }
  }, 1000);
}

if (workoutCards.length > 0) {
  workoutCards.forEach((card) => {
    const key = card.dataset.exerciseKey || card.dataset.exerciseName;
    if (completedSet.has(key)) {
      card.classList.add("done");
    }
  });

  workoutCards.forEach((card, index) => {
    const startBtn = card.querySelector(".workout-start-btn");
    const completeBtn = card.querySelector(".workout-complete-btn");

    if (startBtn) {
      startBtn.addEventListener("click", () => {
        startTimerForCard(index);
      });
    }

    if (completeBtn) {
      completeBtn.addEventListener("click", () => {
        markCardComplete(card, false);
      });
    }
  });

  if (timerStopBtn) {
    timerStopBtn.addEventListener("click", () => {
      stopWorkoutTimer();
    });
  }

  if (timerNextBtn) {
    timerNextBtn.addEventListener("click", () => {
      const nextIndex = activeCardIndex + 1;
      if (nextIndex < workoutCards.length) {
        startTimerForCard(nextIndex);
      } else {
        stopWorkoutTimer();
      }
    });
  }

  updateWorkoutProgress();
}

const modulesGrid = document.getElementById("modules-grid");
const modulesEmpty = document.getElementById("modules-empty");
const moduleSearch = document.getElementById("module-search");
const moduleCategory = document.getElementById("module-category");
const moduleFilterBtn = document.getElementById("module-filter-btn");
const suggestionsBox = document.getElementById("search-suggestions");

let modulesCache = [];
let moodTrendChart = null;
let hydrationChart = null;
let dashboardSummaryCache = null;

function moduleCardHtml(module) {
  const icon = module.icon || "fa-heart";
  const openUrl = module.target_url || `/module/${module.route}`;
  return `
    <article class="glass-panel card-link module-card-anim">
      <i class="fa-solid ${icon} text-fem-600 text-xl"></i>
      <h2>${module.title}</h2>
      <p>${module.description}</p>
      <a href="${openUrl}" class="btn-primary inline-block mt-3">Open Module</a>
    </article>
  `;
}

async function loadDashboardModules() {
  if (!modulesGrid) {
    return;
  }

  const q = encodeURIComponent(moduleSearch?.value?.trim() || "");
  const category = encodeURIComponent(moduleCategory?.value || "all");

  try {
    const response = await fetch(`/api/modules?category=${category}&q=${q}`);
    if (!response.ok) {
      throw new Error("Failed to load modules");
    }

    const payload = await response.json();
    const modules = payload.modules || [];
    modulesCache = modules;
    refreshSuggestionBox();

    if (modules.length === 0) {
      modulesGrid.innerHTML = "";
      modulesEmpty?.classList.remove("hidden");
      return;
    }

    modulesEmpty?.classList.add("hidden");
    modulesGrid.innerHTML = modules.map(moduleCardHtml).join("");
  } catch (_error) {
    modulesGrid.innerHTML = '<p class="text-sm text-rose-600">Unable to load modules right now. Please refresh.</p>';
  }
}

function getSuggestionTerms() {
  const staticTerms = [
    "period",
    "ovulation",
    "mood",
    "stress relief",
    "workout",
    "diet",
    "anxiety support",
    "family wellness",
    "hydration",
  ];

  const moduleTerms = modulesCache.flatMap((module) => [module.title, module.category, module.description]);
  const merged = [...staticTerms, ...moduleTerms]
    .map((item) => String(item || "").trim())
    .filter(Boolean);

  return [...new Set(merged)].slice(0, 40);
}

function refreshSuggestionBox() {
  if (!moduleSearch || !suggestionsBox) {
    return;
  }

  const needle = moduleSearch.value.trim().toLowerCase();
  if (!needle) {
    suggestionsBox.classList.add("hidden");
    suggestionsBox.innerHTML = "";
    return;
  }

  const suggestions = getSuggestionTerms()
    .filter((term) => term.toLowerCase().includes(needle))
    .slice(0, 6);

  if (suggestions.length === 0) {
    suggestionsBox.classList.add("hidden");
    suggestionsBox.innerHTML = "";
    return;
  }

  suggestionsBox.innerHTML = suggestions
    .map((term) => `<button type="button" class="suggestion-item" data-term="${term.replace(/"/g, "&quot;")}">${term}</button>`)
    .join("");
  suggestionsBox.classList.remove("hidden");
}

function renderList(element, items) {
  if (!element) {
    return;
  }
  if (!items || items.length === 0) {
    element.innerHTML = "<li>No entries yet.</li>";
    return;
  }
  element.innerHTML = items.map((item) => `<li>${item}</li>`).join("");
}

function renderCycleTimeline(rows) {
  const list = document.getElementById("cycle-timeline");
  if (!list) {
    return;
  }

  if (!rows || rows.length === 0) {
    list.innerHTML = '<li><span class="timeline-title">No cycle timeline yet</span><span class="timeline-date">Add period data</span></li>';
    return;
  }

  list.innerHTML = rows
    .map(
      (row) =>
        `<li><span class="timeline-title">${row.title || "Cycle event"}</span><span class="timeline-date">${row.date || "Pending"}</span></li>`
    )
    .join("");
}

function renderMoodChart(points) {
  const canvas = document.getElementById("mood-trend-chart");
  if (!canvas || !window.Chart) {
    return;
  }

  if (moodTrendChart) {
    moodTrendChart.destroy();
  }

  moodTrendChart = new Chart(canvas, {
    type: "line",
    data: {
      labels: points.map((point) => point.label),
      datasets: [
        {
          label: "Mood score",
          data: points.map((point) => point.score),
          borderColor: "#7b46e3",
          backgroundColor: "rgba(123, 70, 227, 0.18)",
          fill: true,
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          max: 10,
          ticks: { stepSize: 2 },
          grid: { color: "rgba(137, 82, 255, 0.12)" },
        },
        x: {
          grid: { display: false },
        },
      },
    },
  });
}

function renderHydrationChart(hydration) {
  const canvas = document.getElementById("hydration-chart");
  if (!canvas || !window.Chart) {
    return;
  }

  if (hydrationChart) {
    hydrationChart.destroy();
  }

  const today = hydration?.today_ml || 0;
  const target = hydration?.target_ml || 1;
  const remaining = Math.max(target - today, 0);

  hydrationChart = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Hydrated", "Remaining"],
      datasets: [
        {
          data: [today, remaining],
          backgroundColor: ["#8a57ee", "#ede4ff"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      cutout: "74%",
      plugins: { legend: { display: false } },
      responsive: true,
    },
  });

  const hydrationMeta = document.getElementById("hydration-meta");
  if (hydrationMeta) {
    hydrationMeta.textContent = `${today}ml of ${target}ml target completed. ${remaining}ml to go.`;
  }
}

function renderDashboardSummary(payload) {
  dashboardSummaryCache = payload;
  const user = payload.user || {};
  const insights = payload.insights || {};
  const widgets = payload.widgets || {};
  const onboarding = payload.onboarding || {};

  const greetingEl = document.getElementById("dashboard-greeting");
  const supportNoteEl = document.getElementById("dashboard-support-note");
  const cycleEl = document.getElementById("insight-cycle");
  const moodEl = document.getElementById("insight-mood");
  const energyEl = document.getElementById("insight-energy");

  if (greetingEl) {
    greetingEl.textContent = user.headline || `Good Evening, ${user.name || "there"} 💜`;
  }
  if (supportNoteEl) {
    supportNoteEl.textContent = "Your dashboard adapts to your logs, mood check-ins, and routines.";
  }
  if (cycleEl) {
    cycleEl.textContent = insights.cycle_phase || "Pending";
  }
  if (moodEl) {
    moodEl.textContent = insights.mood_status || "Pending";
  }
  if (energyEl) {
    energyEl.textContent = insights.energy_level || "Pending";
  }

  const nextPeriod = document.getElementById("next-period-date");
  const ovulation = document.getElementById("ovulation-window");
  const dailyTip = document.getElementById("daily-tip");
  if (nextPeriod) {
    nextPeriod.textContent = widgets.next_period_date || "No period data yet";
  }
  if (ovulation) {
    ovulation.textContent = widgets.ovulation_window || "No ovulation estimate yet";
  }
  if (dailyTip) {
    dailyTip.textContent = widgets.daily_tip || "Take a gentle pause and hydrate.";
  }

  const workout = widgets.workout || {};
  const progressFill = document.getElementById("workout-progress-fill");
  const progressText = document.getElementById("workout-progress-text");
  const workoutMeta = document.getElementById("workout-meta");
  if (progressFill) {
    progressFill.style.width = `${workout.progress_percent || 0}%`;
  }
  if (progressText) {
    progressText.textContent = `${workout.progress_percent || 0}% completed`;
  }
  if (workoutMeta) {
    workoutMeta.textContent = `${workout.completed || 0} of ${workout.total || 0} tasks | Streak ${workout.streak || 0}`;
  }

  renderMoodChart(widgets.mood_points || []);
  renderHydrationChart(widgets.hydration || {});
  renderCycleTimeline(payload.cycle_timeline || []);
  renderList(document.getElementById("dashboard-recommendations"), widgets.recommendations || []);
  renderList(document.getElementById("onboarding-tips"), onboarding.tips || []);

  const onboardingPercent = document.getElementById("onboarding-percent");
  const onboardingFill = document.getElementById("onboarding-fill");
  if (onboardingPercent) {
    onboardingPercent.textContent = `${onboarding.completion_percent || 0}%`;
  }
  if (onboardingFill) {
    onboardingFill.style.width = `${onboarding.completion_percent || 0}%`;
  }
}

async function loadDashboardSummary() {
  const root = document.getElementById("dashboard-root");
  if (!root) {
    return;
  }

  try {
    const response = await fetch("/api/dashboard/summary");
    if (!response.ok) {
      throw new Error("summary error");
    }
    const payload = await response.json();
    renderDashboardSummary(payload);
  } catch (_error) {
    const supportNoteEl = document.getElementById("dashboard-support-note");
    if (supportNoteEl) {
      supportNoteEl.textContent = "Could not load personalized summary right now. Please refresh.";
    }
  }
}

function scoreToLabel(score) {
  if (score >= 8) {
    return "Great";
  }
  if (score >= 6) {
    return "Steady";
  }
  if (score >= 4) {
    return "Low";
  }
  return "Needs support";
}

function latestMoodFromSummary(payload) {
  const points = payload?.widgets?.mood_points || [];
  if (points.length === 0) {
    return null;
  }
  return points[points.length - 1];
}

function featureModalConfig(summary) {
  const userName = summary?.user?.name || "You";
  const widgets = summary?.widgets || {};
  const insights = summary?.insights || {};
  const workout = widgets.workout || {};
  const hydration = widgets.hydration || {};
  const todayHydration = hydration.today_ml || 0;
  const targetHydration = hydration.target_ml || 2000;
  const hydrationPercent = Math.min(100, Math.round((todayHydration / Math.max(targetHydration, 1)) * 100));
  const moodPoint = latestMoodFromSummary(summary);
  const moodLabel = moodPoint ? scoreToLabel(Number(moodPoint.score) || 0) : (insights.mood_status || "Pending");

  return {
    period: {
      title: "Period Tracker",
      icon: "fa-calendar-days",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-clock"></i> Next Period</h3>
            <p class="feature-block-text">${widgets.next_period_date || "Add cycle data to get your prediction."}</p>
            <div class="feature-pill-row">
              <span class="feature-pill">Phase: ${insights.cycle_phase || "Pending"}</span>
              <span class="feature-pill">Energy: ${insights.energy_level || "Balanced"}</span>
            </div>
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-circle-dot"></i> Ovulation Window</h3>
            <p class="feature-block-text">${widgets.ovulation_window || "Track period date to estimate ovulation."}</p>
            <ul class="feature-list">
              <li><i class="fa-solid fa-check text-fem-600"></i>Gentle reminder to hydrate and rest well.</li>
              <li><i class="fa-solid fa-check text-fem-600"></i>Log symptoms daily for better accuracy.</li>
            </ul>
          </section>
        </div>
      `,
    },
    pregnancy: {
      title: "Pregnancy Tracker",
      icon: "fa-baby",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-heart"></i> Gentle Daily Check</h3>
            <p class="feature-block-text">Hi ${userName}, track how you feel today for a calmer pregnancy journey.</p>
            <input class="feature-input" type="text" placeholder="How is your energy or appetite today?">
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-shield-heart"></i> Care Focus</h3>
            <ul class="feature-list">
              <li><i class="fa-solid fa-seedling text-fem-600"></i>Balanced hydration and regular meals.</li>
              <li><i class="fa-solid fa-seedling text-fem-600"></i>Watch discomfort trends over the week.</li>
              <li><i class="fa-solid fa-seedling text-fem-600"></i>Use the chatbot for emotional support anytime.</li>
            </ul>
          </section>
        </div>
      `,
    },
    health_checker: {
      title: "Health Checker",
      icon: "fa-stethoscope",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-vial"></i> Symptom Snapshot</h3>
            <input class="feature-input" type="text" placeholder="Enter current symptom for quick guidance...">
            <p class="feature-block-text">This tool provides supportive wellness guidance and not a medical diagnosis.</p>
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-notes-medical"></i> Safety Notes</h3>
            <ul class="feature-list">
              <li><i class="fa-solid fa-circle-exclamation text-fem-600"></i>Seek emergency care for severe symptoms.</li>
              <li><i class="fa-solid fa-circle-exclamation text-fem-600"></i>Use your logs to discuss with clinicians.</li>
            </ul>
          </section>
        </div>
      `,
    },
    tips: {
      title: "Daily Tips",
      icon: "fa-lightbulb",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-star"></i> Personalized Tip</h3>
            <p class="feature-block-text">${widgets.daily_tip || "Take small restorative breaks through the day."}</p>
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-list-check"></i> Quick Wellness Actions</h3>
            <div class="feature-pill-row">
              <span class="feature-pill">2 minute breathing</span>
              <span class="feature-pill">Mindful hydration</span>
              <span class="feature-pill">Stretch reset</span>
            </div>
          </section>
        </div>
      `,
    },
    fitness: {
      title: "Fitness & Diet",
      icon: "fa-dumbbell",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-fire"></i> Workout Progress</h3>
            <p class="feature-block-text">${workout.completed || 0} of ${workout.total || 0} tasks completed.</p>
            <div class="feature-inline-progress"><span style="width:${workout.progress_percent || 0}%"></span></div>
            <p class="feature-block-text">Streak: ${workout.streak || 0} day(s)</p>
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-bowl-food"></i> Diet Focus</h3>
            <ul class="feature-list">
              <li><i class="fa-solid fa-apple-whole text-fem-600"></i>Prioritize iron and protein in meals.</li>
              <li><i class="fa-solid fa-apple-whole text-fem-600"></i>Pair carbs with fiber for steady energy.</li>
            </ul>
          </section>
        </div>
      `,
    },
    workout: {
      title: "Workout Trainer",
      icon: "fa-person-running",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-stopwatch"></i> Session Pulse</h3>
            <p class="feature-block-text">${workout.progress_percent || 0}% session completion with streak ${workout.streak || 0}.</p>
            <div class="feature-inline-progress"><span style="width:${workout.progress_percent || 0}%"></span></div>
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-glass-water"></i> Hydration</h3>
            <p class="feature-block-text">${todayHydration}ml of ${targetHydration}ml</p>
            <div class="feature-inline-progress"><span style="width:${hydrationPercent}%"></span></div>
          </section>
        </div>
      `,
    },
    mood_chat: {
      title: "Mood Chatbot",
      icon: "fa-comments",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-face-smile"></i> Mood Check-in</h3>
            <p class="feature-block-text">Current mood trend: ${moodLabel}</p>
            <input class="feature-input" type="text" placeholder="How are you feeling right now, ${userName}?">
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-heart-circle-plus"></i> Support Topics</h3>
            <div class="feature-pill-row">
              <span class="feature-pill">Stress relief</span>
              <span class="feature-pill">Family concerns</span>
              <span class="feature-pill">Period emotions</span>
              <span class="feature-pill">Motivation</span>
            </div>
          </section>
        </div>
      `,
    },
    diabetes_heart: {
      title: "Diabetes & Heart",
      icon: "fa-heart-pulse",
      html: `
        <div class="feature-modal-grid">
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-chart-line"></i> Risk Awareness</h3>
            <p class="feature-block-text">Track lifestyle patterns regularly for preventive insights and early action.</p>
            <ul class="feature-list">
              <li><i class="fa-solid fa-check text-fem-600"></i>Blood sugar-friendly meal routines.</li>
              <li><i class="fa-solid fa-check text-fem-600"></i>Daily activity and stress balance.</li>
            </ul>
          </section>
          <section class="feature-block">
            <h3 class="feature-block-title"><i class="fa-solid fa-notes-medical"></i> Wellness Disclaimer</h3>
            <p class="feature-block-text">This preview is educational and not a clinical diagnosis. Consult a doctor for medical concerns.</p>
          </section>
        </div>
      `,
    },
  };
}

const featureModalEl = document.getElementById("feature-modal");
const featureModalTitleEl = document.getElementById("feature-modal-title");
const featureModalIconEl = document.getElementById("feature-modal-icon");
const featureModalContentEl = document.getElementById("feature-modal-content");
const featureModalCloseBtn = document.getElementById("feature-modal-close");

async function ensureModalData() {
  if (dashboardSummaryCache) {
    return dashboardSummaryCache;
  }

  try {
    const response = await fetch("/api/dashboard/summary");
    if (!response.ok) {
      throw new Error("summary error");
    }
    const payload = await response.json();
    dashboardSummaryCache = payload;
    return payload;
  } catch (_error) {
    return {};
  }
}

function openFeatureModal(config) {
  if (!featureModalEl || !featureModalTitleEl || !featureModalIconEl || !featureModalContentEl) {
    return;
  }

  featureModalTitleEl.textContent = config.title || "Feature Preview";
  featureModalIconEl.innerHTML = `<i class="fa-solid ${config.icon || "fa-seedling"}"></i>`;
  featureModalContentEl.innerHTML = config.html || "<p class=\"feature-block-text\">No preview available.</p>";
  featureModalEl.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function closeFeatureModal() {
  if (!featureModalEl) {
    return;
  }
  featureModalEl.classList.add("hidden");
  document.body.classList.remove("modal-open");
}

if (featureModalEl) {
  document.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    const modalTrigger = target.closest("[data-dashboard-modal='true']");
    if (!modalTrigger) {
      return;
    }

    event.preventDefault();
    const feature = modalTrigger.dataset.feature;
    if (!feature) {
      return;
    }

    const summary = await ensureModalData();
    const configMap = featureModalConfig(summary);
    const config = configMap[feature];
    if (!config) {
      return;
    }
    openFeatureModal(config);
  });

  featureModalCloseBtn?.addEventListener("click", closeFeatureModal);

  featureModalEl.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    if (target.dataset.modalClose === "true") {
      closeFeatureModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !featureModalEl.classList.contains("hidden")) {
      closeFeatureModal();
    }
  });
}

if (modulesGrid) {
  loadDashboardModules();
  loadDashboardSummary();
  moduleFilterBtn?.addEventListener("click", loadDashboardModules);
  moduleCategory?.addEventListener("change", loadDashboardModules);
  moduleSearch?.addEventListener("input", () => {
    refreshSuggestionBox();
  });
  moduleSearch?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      suggestionsBox?.classList.add("hidden");
      loadDashboardModules();
    }
  });

  suggestionsBox?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    const term = target.dataset.term;
    if (!term || !moduleSearch) {
      return;
    }
    moduleSearch.value = term;
    suggestionsBox.classList.add("hidden");
    loadDashboardModules();
  });

  document.addEventListener("click", (event) => {
    if (!suggestionsBox || !moduleSearch) {
      return;
    }
    if (event.target !== moduleSearch && !suggestionsBox.contains(event.target)) {
      suggestionsBox.classList.add("hidden");
    }
  });
}

const sidebarToggle = document.getElementById("sidebar-toggle");
const sidebarOverlay = document.getElementById("sidebar-overlay");

function syncSidebarOverlay() {
  if (!sidebarOverlay) {
    return;
  }
  const isOpen = document.body.classList.contains("sidebar-open");
  if (isOpen) {
    sidebarOverlay.classList.remove("hidden");
  } else {
    sidebarOverlay.classList.add("hidden");
  }
}

sidebarToggle?.addEventListener("click", () => {
  if (window.innerWidth < 1024) {
    document.body.classList.toggle("sidebar-open");
    syncSidebarOverlay();
    return;
  }
  document.body.classList.toggle("sidebar-collapsed");
});

sidebarOverlay?.addEventListener("click", () => {
  document.body.classList.remove("sidebar-open");
  syncSidebarOverlay();
});

window.addEventListener("resize", () => {
  if (window.innerWidth >= 1024) {
    document.body.classList.remove("sidebar-open");
    syncSidebarOverlay();
  }
});

// Hard guard for stale cached templates: remove legacy cycle snapshot section if it appears.
const legacyCycleHeading = [...document.querySelectorAll("h1, h2, h3, h4")].find(
  (el) => el.textContent.trim().toLowerCase() === "cycle knowledge snapshot"
);
if (legacyCycleHeading) {
  const removeTarget = legacyCycleHeading.closest("article") || legacyCycleHeading.parentElement;
  if (removeTarget) {
    removeTarget.remove();
  }
}
