// app.js
// World Cup Face-Off front-end logic (ES module, no external dependencies).

const FLAG_EMOJI = {
  "USA": "🇺🇸",
  "Canada": "🇨🇦",
  "Mexico": "🇲🇽",
  "Argentina": "🇦🇷",
  "Brazil": "🇧🇷",
  "France": "🇫🇷",
  "England": "\u{1F3F4}\u{E0067}\u{E0062}\u{E0065}\u{E006E}\u{E0067}\u{E007F}",
  "Germany": "🇩🇪",
  "Spain": "🇪🇸",
  "Portugal": "🇵🇹",
  "Netherlands": "🇳🇱",
  "Belgium": "🇧🇪",
  "Croatia": "🇭🇷",
  "Switzerland": "🇨🇭",
  "Uruguay": "🇺🇾",
  "Colombia": "🇨🇴",
  "Ecuador": "🇪🇨",
  "Chile": "🇨🇱",
  "Senegal": "🇸🇳",
  "Morocco": "🇲🇦",
  "Nigeria": "🇳🇬",
  "Cameroon": "🇨🇲",
  "Ghana": "🇬🇭",
  "South Africa": "🇿🇦",
  "Japan": "🇯🇵",
  "South Korea": "🇰🇷",
  "Australia": "🇦🇺",
  "Iran": "🇮🇷",
  "Saudi Arabia": "🇸🇦",
  "Qatar": "🇶🇦",
  "New Zealand": "🇳🇿",
  "Egypt": "🇪🇬",
};

const ANALYSIS_MESSAGES = [
  "Fetching historical match data...",
  "Computing ELO ratings...",
  "Analyzing recent form...",
  "Evaluating head-to-head record...",
  "Consulting team intelligence...",
  "Running prediction model...",
  "Finalizing results...",
];

const THINKING_DURATION_MS = 5000;
const MESSAGE_INTERVAL_MS = 700;
const MODEL_NOTE_TEXT = "Model trained on 49,000+ international matches (1872–2024).";
const STATUS_POLL_INTERVAL_MS = 2000;
const WARMUP_BANNER_TEXT = "Warming up the prediction engine...";

let els = {};
let messageIntervalId = null;
let statusPollIntervalId = null;
let hasShownModelNote = false;

function qs(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function teamLabel(name) {
  const flag = FLAG_EMOJI[name];
  return flag ? `${flag} ${name}` : name;
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

function cacheElements() {
  els = {
    teamASelect: qs("team-a-select"),
    teamBSelect: qs("team-b-select"),
    predictBtn: qs("predict-btn"),

    thinkingSection: qs("thinking-section"),
    thinkingMessage: qs("thinking-message"),
    progressBarFill: qs("progress-bar-fill"),

    resultsSection: qs("results-section"),
    resultTeamAFlag: qs("result-team-a-flag"),
    resultTeamAName: qs("result-team-a-name"),
    resultTeamBFlag: qs("result-team-b-flag"),
    resultTeamBName: qs("result-team-b-name"),

    probTeamALabel: qs("prob-team-a-label"),
    probTeamAValue: qs("prob-team-a-value"),
    probBarA: qs("prob-bar-a"),
    probDrawValue: qs("prob-draw-value"),
    probBarDraw: qs("prob-bar-draw"),
    probTeamBLabel: qs("prob-team-b-label"),
    probTeamBValue: qs("prob-team-b-value"),
    probBarB: qs("prob-bar-b"),

    predictedWinnerText: qs("predicted-winner-text"),
    confidenceBadge: qs("confidence-badge"),

    teamAEloName: qs("team-a-elo-name"),
    teamAEloValue: qs("team-a-elo-value"),
    teamBEloName: qs("team-b-elo-name"),
    teamBEloValue: qs("team-b-elo-value"),

    teamAForm: qs("team-a-form"),
    teamBForm: qs("team-b-form"),

    h2hSummary: qs("h2h-summary"),
    h2hDots: qs("h2h-dots"),

    keyFactorsList: qs("key-factors-list"),

    teamAPlayersCard: qs("team-a-players-card"),
    teamBPlayersCard: qs("team-b-players-card"),

    predictAgainBtn: qs("predict-again-btn"),
    mainEl: document.querySelector("main"),
    siteFooter: document.querySelector(".site-footer"),
  };
}

async function init() {
  cacheElements();

  els.teamASelect.addEventListener("change", updatePredictButtonState);
  els.teamBSelect.addEventListener("change", updatePredictButtonState);
  els.predictBtn.addEventListener("click", handlePredictClick);
  els.predictAgainBtn.addEventListener("click", handlePredictAgain);

  startStatusPolling();

  try {
    const teams = await fetchTeams();
    populateDropdown(els.teamASelect, teams);
    populateDropdown(els.teamBSelect, teams);
  } catch (err) {
    console.error("[app] Failed to load teams:", err);
  }
}

document.addEventListener("DOMContentLoaded", init);

// ---------------------------------------------------------------------------
// Model warm-up status polling
// ---------------------------------------------------------------------------

function ensureWarmupBanner() {
  let banner = qs("warmup-banner");
  if (banner) return banner;

  banner = document.createElement("div");
  banner.id = "warmup-banner";
  banner.className = "warmup-banner hidden";
  banner.setAttribute("role", "status");
  banner.setAttribute("aria-live", "polite");
  banner.textContent = WARMUP_BANNER_TEXT;
  document.body.insertBefore(banner, document.body.firstChild);
  return banner;
}

function showWarmupBanner() {
  ensureWarmupBanner().classList.remove("hidden");
}

function hideWarmupBanner() {
  const banner = qs("warmup-banner");
  if (banner) banner.classList.add("hidden");
}

async function pollModelStatus() {
  try {
    const response = await fetch("/api/status");
    if (!response.ok) return;
    const status = await response.json();

    if (status.model_ready) {
      hideWarmupBanner();
      stopStatusPolling();
    } else {
      showWarmupBanner();
    }
  } catch (err) {
    console.error("[app] Failed to fetch /api/status:", err);
  }
}

function startStatusPolling() {
  showWarmupBanner();
  pollModelStatus();
  statusPollIntervalId = setInterval(pollModelStatus, STATUS_POLL_INTERVAL_MS);
}

function stopStatusPolling() {
  if (statusPollIntervalId !== null) {
    clearInterval(statusPollIntervalId);
    statusPollIntervalId = null;
  }
}

// ---------------------------------------------------------------------------
// Team dropdowns
// ---------------------------------------------------------------------------

async function fetchTeams() {
  const response = await fetch("/api/teams");
  if (!response.ok) {
    throw new Error(`Failed to load teams (status ${response.status})`);
  }
  const data = await response.json();
  return Array.isArray(data.teams) ? data.teams : [];
}

function populateDropdown(select, teams) {
  for (const team of teams) {
    const option = document.createElement("option");
    option.value = team;
    option.textContent = teamLabel(team);
    select.appendChild(option);
  }
}

function updatePredictButtonState() {
  const teamA = els.teamASelect.value;
  const teamB = els.teamBSelect.value;
  els.predictBtn.disabled = !(teamA && teamB && teamA !== teamB);
}

function resetSelections() {
  els.teamASelect.value = "";
  els.teamBSelect.value = "";
  updatePredictButtonState();
}

// ---------------------------------------------------------------------------
// Thinking / loading sequence
// ---------------------------------------------------------------------------

function showThinking() {
  hideError();
  els.resultsSection.classList.add("hidden");
  els.resultsSection.classList.remove("show");

  els.thinkingSection.classList.remove("hidden");
  resetProgressBar();
}

function hideThinking() {
  els.thinkingSection.classList.add("hidden");
  resetProgressBar();
  els.thinkingMessage.classList.remove("fade-out");
}

function resetProgressBar() {
  els.progressBarFill.classList.remove("filling");
  void els.progressBarFill.offsetWidth; // force reflow so the transition restarts cleanly
}

function startProgressBar() {
  resetProgressBar();
  requestAnimationFrame(() => {
    els.progressBarFill.classList.add("filling");
  });
}

function startMessageCycle() {
  let index = 0;
  els.thinkingMessage.textContent = ANALYSIS_MESSAGES[0];
  els.thinkingMessage.classList.remove("fade-out");

  messageIntervalId = setInterval(() => {
    index = (index + 1) % ANALYSIS_MESSAGES.length;
    els.thinkingMessage.classList.add("fade-out");
    setTimeout(() => {
      els.thinkingMessage.textContent = ANALYSIS_MESSAGES[index];
      els.thinkingMessage.classList.remove("fade-out");
    }, 200);
  }, MESSAGE_INTERVAL_MS);
}

function stopMessageCycle() {
  if (messageIntervalId !== null) {
    clearInterval(messageIntervalId);
    messageIntervalId = null;
  }
}

// ---------------------------------------------------------------------------
// Prediction flow
// ---------------------------------------------------------------------------

async function requestPrediction(teamA, teamB) {
  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ team_a: teamA, team_b: teamB }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok || data.error) {
    throw new Error(data.error || `Prediction failed (status ${response.status})`);
  }

  return data;
}

async function handlePredictClick() {
  const teamA = els.teamASelect.value;
  const teamB = els.teamBSelect.value;

  if (!teamA || !teamB || teamA === teamB) {
    return;
  }

  showThinking();
  startProgressBar();
  startMessageCycle();

  // Fired together: the API call begins immediately, the timer runs in parallel.
  const apiPromise = requestPrediction(teamA, teamB);
  const timerPromise = wait(THINKING_DURATION_MS);

  try {
    const [data] = await Promise.all([apiPromise, timerPromise]);
    stopMessageCycle();
    hideThinking();
    renderResults(data);
  } catch (err) {
    stopMessageCycle();
    hideThinking();
    showError(teamA, teamB, err.message);
  }
}

function handlePredictAgain() {
  resetSelections();
  els.resultsSection.classList.add("hidden");
  els.resultsSection.classList.remove("show");
  els.thinkingSection.classList.add("hidden");
  hideError();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ---------------------------------------------------------------------------
// Rendering results
// ---------------------------------------------------------------------------

function renderResults(data) {
  const teamAFlag = data.team_a_flag || FLAG_EMOJI[data.team_a] || "";
  const teamBFlag = data.team_b_flag || FLAG_EMOJI[data.team_b] || "";

  els.resultTeamAFlag.textContent = teamAFlag;
  els.resultTeamAName.textContent = data.team_a;
  els.resultTeamBFlag.textContent = teamBFlag;
  els.resultTeamBName.textContent = data.team_b;

  els.probTeamALabel.textContent = `${data.team_a} Win`;
  els.probTeamBLabel.textContent = `${data.team_b} Win`;
  els.probTeamAValue.textContent = `${data.team_a_win_prob}%`;
  els.probDrawValue.textContent = `${data.draw_prob}%`;
  els.probTeamBValue.textContent = `${data.team_b_win_prob}%`;

  animateProbabilityBar(els.probBarA, data.team_a_win_prob);
  animateProbabilityBar(els.probBarDraw, data.draw_prob);
  animateProbabilityBar(els.probBarB, data.team_b_win_prob);

  renderWinnerAnnouncement(data);

  els.teamAEloName.textContent = data.team_a;
  els.teamAEloValue.textContent = data.team_a_elo;
  els.teamBEloName.textContent = data.team_b;
  els.teamBEloValue.textContent = data.team_b_elo;

  renderFormBlock(els.teamAForm, data.team_a, data.team_a_form);
  renderFormBlock(els.teamBForm, data.team_b, data.team_b_form);

  renderHeadToHead(data);
  renderKeyFactors(data.key_factors || []);

  renderPlayerCard(els.teamAPlayersCard, data.team_a, teamAFlag, data.team_a_players);
  renderPlayerCard(els.teamBPlayersCard, data.team_b, teamBFlag, data.team_b_players);

  showModelNote();

  els.resultsSection.classList.remove("hidden");
  els.resultsSection.classList.remove("show");
  void els.resultsSection.offsetWidth; // force reflow so the slide-up animation restarts
  els.resultsSection.classList.add("show");

  els.resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function animateProbabilityBar(barEl, percent) {
  const value = Number.isFinite(percent) ? percent : 0;
  barEl.style.width = "0%";
  void barEl.offsetWidth; // force reflow so the width transition replays from 0
  requestAnimationFrame(() => {
    barEl.style.width = `${value}%`;
  });
}

function renderWinnerAnnouncement(data) {
  let label;
  let resultClass;

  if (data.predicted_winner === "team_a") {
    label = `${data.team_a} Wins`;
    resultClass = "winner-a";
  } else if (data.predicted_winner === "team_b") {
    label = `${data.team_b} Wins`;
    resultClass = "winner-b";
  } else {
    label = "Draw";
    resultClass = "winner-draw";
  }

  els.predictedWinnerText.textContent = label;
  els.predictedWinnerText.className = `predicted-winner-text ${resultClass}`;

  const confidenceClass = (data.confidence || "Low").toLowerCase();
  els.confidenceBadge.textContent = data.confidence || "Low";
  els.confidenceBadge.className = `confidence-badge ${confidenceClass}`;
}

function renderFormBlock(container, teamName, form) {
  if (!container) return;

  if (!form) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = `
    <div class="form-team-name">${escapeHtml(teamName)}</div>
    <div class="form-stats">
      <span class="form-stat win">${form.wins}W</span>
      <span class="form-stat draw">${form.draws}D</span>
      <span class="form-stat loss">${form.losses}L</span>
    </div>
    <div class="form-mini-bar">${buildFormMiniBar(form)}</div>
    <div class="form-goals">Goals: ${form.goals_scored} scored / ${form.goals_conceded} conceded</div>
  `;
}

function buildFormMiniBar(form) {
  // recent_form() returns aggregate W/D/L counts (not match-by-match order),
  // so the mini bar renders wins, then draws, then losses as colored dots.
  const dots = [];
  for (let i = 0; i < form.wins; i++) dots.push('<span class="mini-dot win"></span>');
  for (let i = 0; i < form.draws; i++) dots.push('<span class="mini-dot draw"></span>');
  for (let i = 0; i < form.losses; i++) dots.push('<span class="mini-dot loss"></span>');
  return dots.join("");
}

function renderHeadToHead(data) {
  const h2h = data.head_to_head || {};
  const total = h2h.total_matches || 0;

  els.h2hSummary.textContent = total > 0
    ? `${data.team_a} ${h2h.team_a_wins}W — ${h2h.draws}D — ${h2h.team_b_wins}W ${data.team_b} (${total} meetings)`
    : `No previous meetings recorded between ${data.team_a} and ${data.team_b}.`;

  els.h2hDots.innerHTML = "";
  const last5 = h2h.last_5_results || [];

  for (const result of last5) {
    const dot = document.createElement("span");
    dot.classList.add("h2h-dot");
    if (result === "A Win") {
      dot.classList.add("win");
    } else if (result === "B Win") {
      dot.classList.add("loss");
    } else {
      dot.classList.add("draw");
    }
    els.h2hDots.appendChild(dot);
  }
}

function renderKeyFactors(factors) {
  els.keyFactorsList.innerHTML = "";
  for (const factor of factors) {
    const li = document.createElement("li");
    li.textContent = factor;
    els.keyFactorsList.appendChild(li);
  }
}

function renderPlayerCard(container, teamName, flagEmoji, squad) {
  if (!container) return;

  const flag = flagEmoji || (squad && squad.flag_emoji) || FLAG_EMOJI[teamName] || "";
  const players = (squad && squad.star_players) || [];

  const playersHtml = players.length
    ? `<ul class="player-list">${players.map(playerItemHtml).join("")}</ul>`
    : `<p class="no-player-data">No squad data available for ${escapeHtml(teamName)}.</p>`;

  container.innerHTML = `
    <div class="players-card-header">
      <span class="players-card-flag">${flag}</span>
      <h3 class="players-card-team">${escapeHtml(teamName)}</h3>
    </div>
    ${playersHtml}
  `;
}

function playerItemHtml(player) {
  return `
    <li class="player-item">
      <span class="player-name">${escapeHtml(player.name)}</span>
      <span class="player-position">${escapeHtml(player.position)}</span>
      <span class="player-club">${escapeHtml(player.club)}</span>
      <span class="player-caps">${player.caps} caps</span>
    </li>
  `;
}

function showModelNote() {
  if (hasShownModelNote || !els.siteFooter) return;
  hasShownModelNote = true;

  const note = document.createElement("p");
  note.id = "model-info-note";
  note.className = "model-info-note";
  note.textContent = MODEL_NOTE_TEXT;
  els.siteFooter.appendChild(note);
}

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

function ensureErrorSection() {
  let section = qs("error-section");
  if (section) return section;

  section = document.createElement("section");
  section.id = "error-section";
  section.className = "error-section hidden";
  section.setAttribute("aria-label", "Prediction error");
  els.mainEl.insertBefore(section, els.resultsSection);
  return section;
}

function showError(teamA, teamB, message) {
  const section = ensureErrorSection();

  section.innerHTML = `
    <p class="error-message">Couldn't generate a prediction for
      <strong>${escapeHtml(teamA)}</strong> vs <strong>${escapeHtml(teamB)}</strong>.
    </p>
    <p class="error-detail">${escapeHtml(message || "An unexpected error occurred.")}</p>
    <button id="error-retry-btn" class="predict-again-btn" type="button">Try Again</button>
  `;
  section.classList.remove("hidden");

  qs("error-retry-btn").addEventListener("click", () => {
    hideError();
    handlePredictClick();
  });

  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hideError() {
  const section = qs("error-section");
  if (section) section.classList.add("hidden");
}
