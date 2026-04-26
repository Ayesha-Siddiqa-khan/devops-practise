const form = document.getElementById("ageForm");
const dobInput = document.getElementById("dob");
const resultEl = document.getElementById("result");
const messageEl = document.getElementById("message");
const historyBody = document.getElementById("historyBody");
const refreshBtn = document.getElementById("refreshBtn");

function setMessage(text, isError = false) {
  messageEl.textContent = text;
  messageEl.classList.toggle("error", isError);
}

function showResult(text) {
  resultEl.textContent = text;
  resultEl.classList.remove("hidden");
}

function clearResult() {
  resultEl.textContent = "";
  resultEl.classList.add("hidden");
}

async function fetchHistory() {
  try {
    const response = await fetch("/history");
    const items = await response.json();

    if (!response.ok) {
      throw new Error("Could not load history.");
    }

    if (!items.length) {
      historyBody.innerHTML = '<tr><td colspan="3" class="empty">No calculations yet.</td></tr>';
      return;
    }

    historyBody.innerHTML = items
      .map(
        (item) =>
          `<tr>
            <td>${item.dob}</td>
            <td>${item.age}</td>
            <td>${item.created_at}</td>
          </tr>`
      )
      .join("");
  } catch (error) {
    historyBody.innerHTML = '<tr><td colspan="3" class="empty">Failed to load history.</td></tr>';
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage("Calculating...");
  clearResult();

  const dob = dobInput.value;

  try {
    const response = await fetch("/calculate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ dob }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Calculation failed.");
    }

    setMessage("Saved successfully.");
    showResult(`Age for ${data.dob} is ${data.age} years.`);
    await fetchHistory();
  } catch (error) {
    setMessage(error.message, true);
  }
});

refreshBtn.addEventListener("click", fetchHistory);

fetchHistory();
