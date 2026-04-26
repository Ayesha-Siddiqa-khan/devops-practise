async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

function renderTrend(containerId, list, formatter) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!list || list.length === 0) {
    container.innerHTML = "<p class='text-slate-500'>No data yet.</p>";
    return;
  }

  const latest = list.slice(-6).reverse();
  container.innerHTML = latest
    .map((item) => `<div class='trend-row'>${item.x}: <strong>${formatter(item)}</strong></div>`)
    .join("");
}

function renderAlerts(alerts) {
  const root = document.getElementById("risk-alerts");
  if (!root) return;

  if (!alerts || alerts.length === 0) {
    root.innerHTML = "<div class='status-card status-normal'>No critical alerts right now.</div>";
    return;
  }

  root.innerHTML = alerts
    .map((alert) => {
      const cls = alert.type === "critical" ? "status-emergency" : "status-monitor";
      return `<div class='status-card ${cls}'>${alert.message}</div>`;
    })
    .join("");
}

function renderTimeline(entries) {
  const root = document.getElementById("health-timeline");
  if (!root) return;

  if (!entries || entries.length === 0) {
    root.innerHTML = "<p class='text-slate-500'>No timeline entries yet.</p>";
    return;
  }

  root.innerHTML = entries
    .map(
      (item) =>
        `<div class='tip-card'><p class='text-xs text-slate-500'>${item.time}</p><p><strong>${item.metric}</strong> - ${item.value} ${item.extra || ""}</p><p class='text-xs text-slate-500'>${item.context || ""}</p></div>`
    )
    .join("");
}

async function refreshInsights() {
  try {
    const response = await fetch("/api/insights");
    const data = await response.json();

    renderTrend("trend-glucose", data.trends?.glucose || [], (item) => `${item.y1} mg/dL (${item.context || ""})`);
    renderTrend("trend-bp", data.trends?.blood_pressure || [], (item) => `${item.y1}/${item.y2} mmHg`);
    renderTrend("trend-weight", data.trends?.weight || [], (item) => `${item.y1} kg`);
    renderAlerts(data.alerts || []);
    renderTimeline(data.timeline || []);
  } catch (_error) {
    // No-op for UI resilience.
  }
}

function setupButtons() {
  const bind = (id, handler) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", handler);
  };

  bind("save-glucose", async () => {
    try {
      await postJson("/api/diabetes/log", {
        reading_type: document.getElementById("glucose-type")?.value,
        value: document.getElementById("glucose-value")?.value,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("save-bp", async () => {
    try {
      await postJson("/api/heart/metrics", {
        metric_type: "blood_pressure",
        systolic: document.getElementById("bp-systolic")?.value,
        diastolic: document.getElementById("bp-diastolic")?.value,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("save-heart-rate", async () => {
    try {
      await postJson("/api/heart/metrics", {
        metric_type: "heart_rate",
        value: document.getElementById("heart-rate")?.value,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("save-weight", async () => {
    try {
      await postJson("/api/heart/metrics", {
        metric_type: "weight",
        value: document.getElementById("weight-value")?.value,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("save-activity", async () => {
    try {
      await postJson("/api/heart/metrics", {
        metric_type: "activity",
        value: document.getElementById("activity-steps")?.value,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("save-meal", async () => {
    try {
      await postJson("/api/meal/log", {
        meal_type: document.getElementById("meal-type")?.value,
        foods: document.getElementById("meal-foods")?.value,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("save-medication", async () => {
    try {
      await postJson("/api/medication/log", {
        medicine_name: document.getElementById("med-name")?.value,
        dosage: document.getElementById("med-dosage")?.value,
        schedule_time: document.getElementById("med-time")?.value,
        reminder_enabled: true,
      });
      await refreshInsights();
    } catch (error) {
      alert(error.message);
    }
  });

  bind("assistant-ask", async () => {
    const q = document.getElementById("assistant-question")?.value || "";
    const replyRoot = document.getElementById("assistant-reply");

    try {
      const data = await postJson("/api/assistant/query", { question: q });
      if (replyRoot) {
        replyRoot.innerHTML = `<p>${data.reply}</p><p class='text-xs text-slate-500 mt-2'>${data.disclaimer}</p>`;
      }
    } catch (error) {
      if (replyRoot) {
        replyRoot.textContent = error.message;
      }
    }
  });
}

if (window.location.pathname.includes("/diabetes-heart")) {
  setupButtons();
  refreshInsights();
}
