"""
build_idas.py — Generates the complete, upgraded Agri-Logistics IDAS index.html
All 10 improvements included:
 1. Robust NLP fallback chain (language → urdu → english)
 2. Dual OSRM routing (fastest + shortest) with toggle
 3. Dynamic fuel cost calculator (PKR)
 4. CartoDB Dark Matter (driver) + Positron (corporate) premium tiles
 5. 4-card metrics dashboard with delta indicators
 6. Mobile-first layout (360px friendly)
 7. Deep emerald + dark gray premium theme
 8. Professional Agri-IDAS v3.0 header, no generic branding
 9. Smooth micro-animations (fade, slide, pulse)
10. speechSynthesis language fix (Sindhi/Urdu/English)
"""

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Agri-IDAS v3.0 | Intelligent Dispatch & Advisory System</title>
<meta name="description" content="Agri-IDAS — Trilingual AI-powered logistics dispatch system for Sindh agricultural transport. Real-time GIS routing, NLP chatbot, IoT telemetry.">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
/* ─── DESIGN TOKENS ──────────────────────────────────────────────── */
:root {
  --em:        #065f46;   /* deep emerald */
  --em-md:     #047857;
  --em-lt:     #10b981;   /* emerald light */
  --em-xs:     #d1fae5;   /* emerald tint */
  --surf:      #0f172a;   /* dark surface */
  --surf2:     #1e293b;
  --surf3:     #334155;
  --surf4:     #475569;
  --text:      #f1f5f9;
  --text2:     #94a3b8;
  --text3:     #64748b;
  --amber:     #d97706;
  --amber-lt:  #fbbf24;
  --red:       #ef4444;
  --blue:      #3b82f6;
  --radius:    14px;
  --radius-sm: 8px;
  --shadow:    0 4px 24px rgba(0,0,0,0.35);
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.25);
  --font-main: 'Inter', sans-serif;
  --font-head: 'Space Grotesk', sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--font-main);
  background: var(--surf);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ─── SCROLLBAR ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surf2); }
::-webkit-scrollbar-thumb { background: var(--em-md); border-radius: 3px; }

/* ─── ANIMATIONS ─────────────────────────────────────────────────── */
@keyframes fadeUp   { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
@keyframes slideIn  { from { opacity:0; transform:translateX(-16px); } to { opacity:1; transform:translateX(0); } }
@keyframes pulse    { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
@keyframes shimmer  { from { background-position: -200% 0; } to { background-position: 200% 0; } }
.anim-fadeup  { animation: fadeUp  0.4s ease both; }
.anim-slidein { animation: slideIn 0.3s ease both; }

/* ─── HEADER / NAV ───────────────────────────────────────────────── */
header.topbar {
  position: sticky; top: 0; z-index: 100;
  background: var(--surf2);
  border-bottom: 1px solid var(--surf3);
  padding: 0 16px;
  height: 56px;
  display: flex; align-items: center; justify-content: space-between;
  backdrop-filter: blur(12px);
}
.topbar-brand {
  font-family: var(--font-head);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--em-lt);
  display: flex; align-items: center; gap: 10px;
}
.topbar-brand .badge {
  font-size: 0.6rem; font-weight: 600;
  background: var(--em); color: var(--em-lt);
  padding: 2px 7px; border-radius: 20px;
  letter-spacing: 0.05em;
}
.live-dot {
  width: 8px; height: 8px;
  background: var(--em-lt);
  border-radius: 50%;
  animation: pulse 1.8s infinite;
}
.topbar-right {
  display: flex; align-items: center; gap: 12px;
}
.topbar-right .trk-chip {
  font-size: 0.75rem; font-weight: 600;
  color: var(--amber-lt);
  background: rgba(217,119,6,0.15);
  border: 1px solid rgba(217,119,6,0.3);
  padding: 4px 10px; border-radius: 20px;
}
.lang-select {
  background: var(--surf3); color: var(--text);
  border: 1px solid var(--surf4); border-radius: 8px;
  padding: 4px 8px; font-size: 0.75rem;
  cursor: pointer; outline: none;
}

/* ─── METRICS BAR ────────────────────────────────────────────────── */
.metrics-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 12px 16px;
  background: var(--surf2);
  border-bottom: 1px solid var(--surf3);
}
@media(max-width:640px) {
  .metrics-bar { grid-template-columns: repeat(2, 1fr); }
}
.metric-card {
  background: var(--surf3);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  border: 1px solid var(--surf4);
  transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform: translateY(-2px); border-color: var(--em-lt); }
.metric-label {
  font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--text3); margin-bottom: 4px;
}
.metric-value {
  font-family: var(--font-head);
  font-size: 1.25rem; font-weight: 700;
  color: var(--text); line-height: 1;
}
.metric-delta {
  font-size: 0.7rem; margin-top: 3px;
  display: flex; align-items: center; gap: 3px;
}
.delta-up   { color: var(--em-lt); }
.delta-down { color: var(--red); }
.delta-neu  { color: var(--text3); }

/* ─── ROUTE TOGGLE ───────────────────────────────────────────────── */
.route-toggle-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  background: var(--surf2);
  border-bottom: 1px solid var(--surf3);
  flex-wrap: wrap;
}
.route-toggle-bar .label {
  font-size: 0.72rem; font-weight: 600;
  color: var(--text2); text-transform: uppercase;
  letter-spacing: 0.06em;
}
.route-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: 20px;
  font-size: 0.78rem; font-weight: 600;
  border: 2px solid transparent;
  cursor: pointer; transition: all 0.2s;
  background: var(--surf3); color: var(--text2);
}
.route-btn.active-r1 {
  background: rgba(16,185,129,0.15);
  border-color: var(--em-lt); color: var(--em-lt);
}
.route-btn.active-r2 {
  background: rgba(59,130,246,0.15);
  border-color: var(--blue); color: var(--blue);
}
.route-dot { width: 10px; height: 10px; border-radius: 50%; }
.route-dot.r1 { background: var(--em-lt); }
.route-dot.r2 { background: var(--blue); }
.route-badge {
  font-size: 0.65rem; font-weight: 700;
  padding: 1px 6px; border-radius: 10px;
  margin-left: 2px;
}
.fuel-display {
  margin-left: auto;
  font-size: 0.78rem; font-weight: 600;
  color: var(--amber-lt);
  display: flex; align-items: center; gap: 5px;
}

/* ─── MAIN LAYOUT ────────────────────────────────────────────────── */
.main-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: calc(100vh - 56px - 72px - 46px);
  min-height: 400px;
}
@media(max-width:768px) {
  .main-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
}

/* ─── TAB PANEL ──────────────────────────────────────────────────── */
.panel {
  display: flex; flex-direction: column;
  border-right: 1px solid var(--surf3);
  overflow: hidden;
}
.panel:last-child { border-right: none; }
.panel-header {
  padding: 10px 14px;
  background: var(--surf2);
  border-bottom: 1px solid var(--surf3);
  display: flex; align-items: center; gap: 8px;
  flex-shrink: 0;
}
.panel-title {
  font-size: 0.78rem; font-weight: 700;
  letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--text2);
}
.panel-icon { font-size: 1rem; }
.map-container {
  flex: 1; min-height: 300px;
}
#map-corp, #map-drv { width:100%; height:100%; }

/* ─── CONTROLS BELOW MAP ─────────────────────────────────────────── */
.controls-bar {
  padding: 8px 12px;
  background: var(--surf2);
  border-top: 1px solid var(--surf3);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  flex-shrink: 0;
}
.ctrl-label { font-size: 0.68rem; color: var(--text3); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.ctrl-slider { flex:1; min-width: 80px; accent-color: var(--em-lt); cursor: pointer; }
.ctrl-value { font-size: 0.72rem; color: var(--em-lt); font-weight: 700; min-width: 28px; }
.ctrl-btn {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem; font-weight: 600;
  cursor: pointer; border: 1px solid;
  transition: all 0.2s;
}
.ctrl-btn.weather { background: rgba(59,130,246,0.15); border-color: var(--blue); color: var(--blue); }
.ctrl-btn.time    { background: rgba(100,116,139,0.15); border-color: var(--surf4); color: var(--text2); }

/* ─── CHAT PANEL ─────────────────────────────────────────────────── */
.chat-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid var(--surf3);
  height: 280px;
}
@media(max-width:768px) {
  .chat-section { grid-template-columns: 1fr; height: auto; }
}
.chat-panel {
  display: flex; flex-direction: column;
  border-right: 1px solid var(--surf3);
  overflow: hidden;
}
.chat-panel:last-child { border-right: none; }
.chat-box {
  flex: 1; overflow-y: auto;
  padding: 8px 12px;
  display: flex; flex-direction: column; gap: 8px;
}
.chat-row {
  display: flex; gap: 8px; align-items: flex-start;
  animation: fadeUp 0.3s ease both;
}
.chat-row.corporate { flex-direction: row-reverse; }
.chat-avatar {
  font-size: 1.1rem; flex-shrink: 0;
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  background: var(--surf3); border-radius: 50%;
}
.chat-bubble {
  background: var(--surf3);
  padding: 7px 11px;
  border-radius: 12px 12px 12px 2px;
  font-size: 0.75rem; line-height: 1.5;
  color: var(--text); max-width: 82%;
  border: 1px solid var(--surf4);
}
.chat-row.corporate .chat-bubble {
  background: rgba(6,95,70,0.25);
  border-color: rgba(16,185,129,0.3);
  border-radius: 12px 12px 2px 12px;
}
.chat-meta {
  font-size: 0.6rem; color: var(--text3); margin-top: 2px;
}
.chat-input-bar {
  padding: 8px 10px;
  border-top: 1px solid var(--surf3);
  display: flex; gap: 6px;
  flex-shrink: 0;
}
.chat-input {
  flex: 1; background: var(--surf3); color: var(--text);
  border: 1px solid var(--surf4); border-radius: 20px;
  padding: 6px 14px; font-size: 0.78rem;
  outline: none; transition: border-color 0.2s;
  font-family: var(--font-main);
}
.chat-input:focus { border-color: var(--em-lt); }
.chat-send {
  background: var(--em); color: white;
  border: none; border-radius: 20px;
  padding: 6px 14px; font-size: 0.78rem; font-weight: 600;
  cursor: pointer; transition: background 0.2s;
  white-space: nowrap;
}
.chat-send:hover { background: var(--em-md); }

/* ─── SAFETY ALERT BANNER ────────────────────────────────────────── */
.safety-banner {
  padding: 8px 16px;
  font-size: 0.75rem; font-weight: 600;
  display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--surf3);
  transition: all 0.3s;
}
.safety-banner.extreme { background: rgba(239,68,68,0.15); color: #fca5a5; }
.safety-banner.critical { background: rgba(217,119,6,0.15); color: var(--amber-lt); }
.safety-banner.warning  { background: rgba(234,179,8,0.12); color: #fde047; }
.safety-banner.standard { background: rgba(16,185,129,0.1); color: var(--em-lt); }

/* ─── MOBILE RESPONSIVE TWEAKS ───────────────────────────────────── */
@media(max-width:480px) {
  .main-layout { min-height: 300px; }
  .metric-value { font-size: 1rem; }
  .chat-section { height: auto; }
  .chat-box { min-height: 150px; max-height: 200px; }
  .topbar-brand .badge { display: none; }
}

/* ─── LOADING OVERLAY ────────────────────────────────────────────── */
.map-loading {
  position: absolute; inset: 0; z-index: 500;
  background: var(--surf2);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 12px;
}
.map-loading .spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--surf3);
  border-top-color: var(--em-lt);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.map-loading p { font-size: 0.8rem; color: var(--text3); }

/* ─── LEAFLET POPUP OVERRIDE ─────────────────────────────────────── */
.leaflet-popup-content-wrapper {
  background: var(--surf2) !important;
  color: var(--text) !important;
  border: 1px solid var(--surf3) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: var(--shadow) !important;
}
.leaflet-popup-tip { background: var(--surf2) !important; }
</style>
</head>
<body>

<!-- ═══════════════════════════════════════════════════════════════
     HEADER
════════════════════════════════════════════════════════════════ -->
<header class="topbar">
  <div class="topbar-brand">
    <span>🌾</span>
    <span>Agri-IDAS</span>
    <span class="badge">v3.0</span>
    <span class="live-dot"></span>
  </div>
  <div class="topbar-right">
    <span class="trk-chip">🚚 TRK-119 · LIVE</span>
    <select class="lang-select" id="lang-sel" onchange="setLang(this.value)">
      <option value="Sindhi">Sindhi سنڌي</option>
      <option value="Urdu">Urdu اردو</option>
      <option value="English" selected>English</option>
      <option value="Dhatki">Dhatki ڌاٽڪي</option>
    </select>
  </div>
</header>

<!-- ═══════════════════════════════════════════════════════════════
     SAFETY BANNER
════════════════════════════════════════════════════════════════ -->
<div class="safety-banner extreme" id="safety-banner">
  <span>⛔</span>
  <span id="safety-text">INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal — Raftar 50% ghat karo</span>
</div>

<!-- ═══════════════════════════════════════════════════════════════
     METRICS BAR
════════════════════════════════════════════════════════════════ -->
<div class="metrics-bar">
  <div class="metric-card">
    <div class="metric-label">Route Distance</div>
    <div class="metric-value" id="m-dist">162.5 km</div>
    <div class="metric-delta delta-neu">📍 Mithi → Hyderabad</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">ETA Remaining</div>
    <div class="metric-value" id="m-eta">3h 15m</div>
    <div class="metric-delta delta-up" id="m-eta-delta">▼ On Schedule</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Fuel Cost (PKR)</div>
    <div class="metric-value" id="m-fuel">Rs. 5,718</div>
    <div class="metric-delta delta-neu" id="m-fuel-note">@ Rs.282/L · 8km/L</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Safety Score</div>
    <div class="metric-value" id="m-safety" style="color:var(--red)">48 %</div>
    <div class="metric-delta delta-down" id="m-safety-delta">▼ Rain + Night Risk</div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════
     ROUTE TOGGLE BAR
════════════════════════════════════════════════════════════════ -->
<div class="route-toggle-bar">
  <span class="label">Route:</span>
  <button class="route-btn active-r1" id="btn-r1" onclick="selectRoute(1)">
    <span class="route-dot r1"></span>
    Route 1 — Fastest
    <span class="route-badge" id="r1-badge" style="background:rgba(16,185,129,0.2);color:var(--em-lt)"></span>
  </button>
  <button class="route-btn" id="btn-r2" onclick="selectRoute(2)">
    <span class="route-dot r2"></span>
    Route 2 — Shortest
    <span class="route-badge" id="r2-badge" style="background:rgba(59,130,246,0.2);color:var(--blue)"></span>
  </button>
  <div class="fuel-display">
    ⛽ <span id="fuel-inline">Rs. 5,718</span>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════
     MAIN MAP LAYOUT
════════════════════════════════════════════════════════════════ -->
<div class="main-layout">

  <!-- Corporate Panel -->
  <div class="panel">
    <div class="panel-header">
      <span class="panel-icon">🏢</span>
      <span class="panel-title">Corporate Dispatch — Bird's Eye View</span>
    </div>
    <div class="map-container" style="position:relative">
      <div class="map-loading" id="corp-loading">
        <div class="spinner"></div>
        <p>Loading CartoDB Positron…</p>
      </div>
      <div id="map-corp" style="width:100%;height:100%"></div>
    </div>
    <div class="controls-bar">
      <span class="ctrl-label">Progress</span>
      <input class="ctrl-slider" type="range" min="0" max="100" value="35" id="progress-slider" oninput="updateProgress(this.value)">
      <span class="ctrl-value" id="progress-val">35%</span>
      <button class="ctrl-btn weather" id="btn-weather" onclick="toggleWeather()">🌧 Rain</button>
      <button class="ctrl-btn time"    id="btn-time"    onclick="toggleTime()">🌙 Night</button>
      <select style="background:var(--surf3);color:var(--text);border:1px solid var(--surf4);border-radius:6px;padding:3px 6px;font-size:0.7rem;" onchange="setCargo(this.value)">
        <option>Tomatoes</option>
        <option>Onions</option>
        <option>Cotton</option>
        <option>Wheat</option>
      </select>
    </div>
  </div>

  <!-- Driver Panel -->
  <div class="panel">
    <div class="panel-header">
      <span class="panel-icon">🚚</span>
      <span class="panel-title">Driver Navigation — Dark Mode</span>
    </div>
    <div class="map-container" style="position:relative">
      <div class="map-loading" id="drv-loading">
        <div class="spinner"></div>
        <p>Loading CartoDB Dark Matter…</p>
      </div>
      <div id="map-drv" style="width:100%;height:100%"></div>
    </div>
    <div class="controls-bar">
      <span class="ctrl-label">Speed</span>
      <span style="font-size:0.78rem;color:var(--em-lt);font-weight:700;" id="spd-display">42 km/h</span>
      <span class="ctrl-label" style="margin-left:8px">Temp</span>
      <span style="font-size:0.78rem;color:var(--amber-lt);font-weight:700;">19.2°C</span>
      <span class="ctrl-label" style="margin-left:8px">μ</span>
      <span style="font-size:0.78rem;color:var(--red);font-weight:700;">0.38 (Wet)</span>
      <button class="ctrl-btn" style="margin-left:auto;background:rgba(16,185,129,0.15);border-color:var(--em-lt);color:var(--em-lt);" onclick="speakAlert()">🔊 Voice Alert</button>
    </div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════
     CHAT SECTION
════════════════════════════════════════════════════════════════ -->
<div class="chat-section">

  <!-- Corporate Chat -->
  <div class="chat-panel">
    <div class="panel-header">
      <span class="panel-icon">🏢</span>
      <span class="panel-title">Corporate Dispatch View</span>
    </div>
    <div class="chat-box" id="corp-chat-box"></div>
    <form class="chat-input-bar" onsubmit="sendCorpMessage(event)">
      <input class="chat-input" id="corp-chat-input" placeholder="Send dispatch advisory…" autocomplete="off">
      <button type="submit" class="chat-send">Send ▶</button>
    </form>
  </div>

  <!-- Driver Chat -->
  <div class="chat-panel">
    <div class="panel-header">
      <span class="panel-icon">🚚</span>
      <span class="panel-title">Driver Communication</span>
    </div>
    <div class="chat-box" id="drv-chat-box"></div>
    <form class="chat-input-bar" onsubmit="sendDrvMessage(event)">
      <input class="chat-input" id="drv-chat-input" placeholder="Type in any language…" autocomplete="off">
      <button type="submit" class="chat-send">Send ▶</button>
    </form>
  </div>

</div>

<!-- ═══════════════════════════════════════════════════════════════
     JAVASCRIPT ENGINE
════════════════════════════════════════════════════════════════ -->
<script>
'use strict';

// ── GLOBAL STATE ─────────────────────────────────────────────────
const state = {
  lang: 'English',
  weather: 'Rain',
  time: 'Night',
  cargo: 'Tomatoes',
  progressPct: 35,
  activeRoute: 1,
  routeData: { r1: null, r2: null },
  messages: []
};

// ── FUEL COST CALCULATOR ─────────────────────────────────────────
const FUEL_PRICE_PKR = 282;   // PKR per litre
const FUEL_EFFICIENCY = 8;    // km per litre

function calcFuelCost(km) {
  const litres = km / FUEL_EFFICIENCY;
  return Math.round(litres * FUEL_PRICE_PKR);
}

function fmtCost(pkr) {
  return 'Rs. ' + pkr.toLocaleString('en-PK');
}

// ── ROUTE METRICS UPDATE ─────────────────────────────────────────
function updateMetrics() {
  const route = state.routeData['r' + state.activeRoute];
  const totalKm = route ? parseFloat((route.distance / 1000).toFixed(1)) : 162.5;
  const remKm   = parseFloat((totalKm * (1 - state.progressPct / 100)).toFixed(1));

  // ETA: assume avg 50 km/h baseline adjusted for conditions
  let avgSpeed = 65;
  if (state.weather === 'Rain' && state.time === 'Night') avgSpeed = 42;
  else if (state.weather === 'Rain' || state.time === 'Night') avgSpeed = 55;
  const remMin = Math.round((remKm / avgSpeed) * 60);
  const hrs    = Math.floor(remMin / 60);
  const mins   = remMin % 60;

  // Safety score
  let safety = 88;
  if (state.weather === 'Rain') safety -= 22;
  if (state.time === 'Night')   safety -= 20;
  if (state.cargo === 'Tomatoes') safety -= 5;
  safety = Math.max(safety, 20);

  const fuelCost = calcFuelCost(totalKm);

  document.getElementById('m-dist').textContent  = totalKm + ' km';
  document.getElementById('m-eta').textContent    = hrs + 'h ' + mins + 'm';
  document.getElementById('m-fuel').textContent   = fmtCost(fuelCost);
  document.getElementById('m-safety').textContent = safety + ' %';
  document.getElementById('m-safety').style.color = safety < 50 ? 'var(--red)' : safety < 70 ? 'var(--amber-lt)' : 'var(--em-lt)';
  document.getElementById('m-eta-delta').textContent  = avgSpeed < 50 ? '▼ Slow — Adverse Conditions' : '▼ On Schedule';
  document.getElementById('m-safety-delta').className = 'metric-delta ' + (safety < 50 ? 'delta-down' : 'delta-up');
  document.getElementById('m-safety-delta').textContent = safety < 50 ? '▼ Rain + Night Risk' : '▲ Safe Driving';
  document.getElementById('fuel-inline').textContent  = fmtCost(fuelCost);
  document.getElementById('spd-display').textContent  = avgSpeed + ' km/h';

  // Route badges
  if (state.routeData.r1) {
    const d1 = (state.routeData.r1.distance / 1000).toFixed(0);
    const t1 = Math.round(state.routeData.r1.duration / 60);
    document.getElementById('r1-badge').textContent = d1 + 'km · ' + t1 + 'min';
  }
  if (state.routeData.r2) {
    const d2 = (state.routeData.r2.distance / 1000).toFixed(0);
    const t2 = Math.round(state.routeData.r2.duration / 60);
    document.getElementById('r2-badge').textContent = d2 + 'km · ' + t2 + 'min';
  }

  // Safety banner
  updateSafetyBanner();
}

function updateSafetyBanner() {
  const el = document.getElementById('safety-banner');
  const txt = document.getElementById('safety-text');
  const lang = state.lang;
  if (state.weather === 'Rain' && state.time === 'Night') {
    el.className = 'safety-banner extreme';
    txt.textContent = {
      English: '⛔ EXTREME RISK: Night + Rain + Fragile Cargo — Reduce speed 50%. Hazard lights ON.',
      Sindhi:  '⛔ INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal — Raftar 50% ghat karo. Hazard lights hinner.',
      Urdu:    '⛔ ANTEHAI KHATARNAK: Raat + Baarish + Nazuk Maal — Raftar 50% ghatayein. Hazard lights on rakhein.',
      Dhatki:  '⛔ BAHUT KHATRO: Raat + Barish + Nazuk Maal — Raftar 50% ghat karo.'
    }[lang] || '⛔ EXTREME RISK: Night + Rain — Reduce speed.';
  } else if (state.weather === 'Rain') {
    el.className = 'safety-banner critical';
    txt.textContent = {
      English: '🛑 CRITICAL: Rain on Highway — Slippery road (μ=0.38). Speed limit 60 km/h.',
      Sindhi:  '🛑 KHATARNAK: Highway te barish — Sadak chikani ahe. Raftar 60 km/h.',
      Urdu:    '🛑 KHATARNAK: Highway par baarish — Sadak phislan wali. Raftar 60 km/h.',
      Dhatki:  '🛑 KHATARNAK: Barish waro raah — Sadak chikani. Raftar 60 km/h.'
    }[lang] || '🛑 CRITICAL: Slippery road. Slow down.';
  } else if (state.time === 'Night') {
    el.className = 'safety-banner warning';
    txt.textContent = {
      English: '⚠️ WARNING: Night driving — Reduce speed to 60 km/h. High-beam headlights ON.',
      Sindhi:  '⚠️ KHABARDAR: Raat driving — Raftar 60 km/h. Headlights tez chalao.',
      Urdu:    '⚠️ KHABARDAR: Raat ko gaari — Raftar 60 km/h. Headlights tez rakhein.',
      Dhatki:  '⚠️ KHABARDAR: Raat driving — Raftar 60 km/h. Headlights tez karo.'
    }[lang] || '⚠️ Night driving. Reduce speed.';
  } else {
    el.className = 'safety-banner standard';
    txt.textContent = {
      English: '✅ STANDARD CONDITIONS: Road clear. Maintain speed limit. Drive safe!',
      Sindhi:  '✅ MAMULI HALAT: Rasto saaf ahe. Speed limit manno. Salaamti halo!',
      Urdu:    '✅ MAMULI HALAT: Rasta saaf hai. Speed limit manein. Salamti se chalein!',
      Dhatki:  '✅ MAMULI HALAT: Raah saaf hai. Raftar limit manno. Salaamti vanj!'
    }[lang] || '✅ Clear conditions. Drive safe.';
  }
}

// ── MAPS INIT ─────────────────────────────────────────────────────
let mapCorp, mapDrv;
let polyR1Corp, polyR2Corp, polyR1Drv, polyR2Drv;
let markerStartCorp, markerEndCorp, markerStartDrv, markerEndDrv;
let progressMarkerCorp, progressMarkerDrv;

// Fallback static route (1,313 OSRM points) – a subset for brevity
const FALLBACK_COORDS = [
  [24.7437, 69.7961],[24.7901, 69.7568],[24.8430, 69.6910],[24.8450, 69.4990],
  [24.8370, 69.4150],[24.8590, 69.3870],[24.8880, 69.3460],[24.9294, 69.3131],
  [24.9706, 69.2970],[25.0148, 69.2806],[25.0938, 69.1842],[25.1577, 69.1021],
  [25.1572, 69.0275],[25.1093, 69.0185],[25.0930, 69.0071],[25.1020, 68.9866],
  [25.1282, 68.9798],[25.1491, 68.9569],[25.1748, 68.8294],[25.2036, 68.7909],
  [25.2199, 68.7350],[25.2211, 68.7237],[25.2630, 68.6526],[25.2990, 68.5841],
  [25.3432, 68.5197],[25.3870, 68.4027],[25.3960, 68.3578]
];

function initMaps() {
  const corpTile = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
  const drvTile  = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
  const attrib   = '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/">OSM</a>';

  mapCorp = L.map('map-corp', { zoomControl: true }).setView([25.07, 69.10], 8);
  L.tileLayer(corpTile, { attribution: attrib, maxZoom: 19, subdomains: 'abcd' }).addTo(mapCorp);

  mapDrv = L.map('map-drv', { zoomControl: false }).setView([25.07, 69.10], 8);
  L.tileLayer(drvTile, { attribution: attrib, maxZoom: 19, subdomains: 'abcd' }).addTo(mapDrv);
  L.control.zoom({ position: 'bottomright' }).addTo(mapDrv);

  // Start/End markers
  const iconStart = L.divIcon({ html: '<div style="background:var(--em-lt);width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px rgba(16,185,129,0.8)"></div>', iconAnchor:[6,6], className:'' });
  const iconEnd   = L.divIcon({ html: '<div style="background:var(--red);width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px rgba(239,68,68,0.8)"></div>', iconAnchor:[6,6], className:'' });

  markerStartCorp = L.marker([24.7437, 69.7961], { icon: iconStart }).addTo(mapCorp).bindPopup('<b>Mithi</b><br>Departure Point');
  markerEndCorp   = L.marker([25.3960, 68.3578], { icon: iconEnd   }).addTo(mapCorp).bindPopup('<b>Hyderabad</b><br>Destination');
  markerStartDrv  = L.marker([24.7437, 69.7961], { icon: iconStart }).addTo(mapDrv).bindPopup('<b>Mithi</b><br>Departure');
  markerEndDrv    = L.marker([25.3960, 68.3578], { icon: iconEnd   }).addTo(mapDrv).bindPopup('<b>Hyderabad</b><br>Destination');

  // Draw fallback static route immediately
  polyR1Corp = L.polyline(FALLBACK_COORDS, { color: '#10b981', weight: 5, opacity: 0.85 }).addTo(mapCorp);
  polyR1Drv  = L.polyline(FALLBACK_COORDS, { color: '#10b981', weight: 5, opacity: 0.85 }).addTo(mapDrv);

  // Hide loading overlays now maps are ready
  document.getElementById('corp-loading').style.display = 'none';
  document.getElementById('drv-loading').style.display  = 'none';

  // Attempt to fetch real dual OSRM routes
  loadDualRoutes();

  setTimeout(() => {
    mapCorp.invalidateSize();
    mapDrv.invalidateSize();
  }, 200);
}

// ── DUAL OSRM ROUTING ─────────────────────────────────────────────
async function loadDualRoutes() {
  const waypoints = '69.7961,24.7436;69.0125,25.1023;68.3578,25.3960';

  // Route 1 — Fastest (default)
  const urlR1 = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;
  // Route 2 — Shortest (use alternatives flag if available, or re-route via different waypoints)
  const urlR2 = `https://router.project-osrm.org/route/v1/driving/69.7961,24.7436;69.5011,24.8580;69.2500,24.9800;68.3578,25.3960?overview=full&geometries=geojson`;

  try {
    const [res1, res2] = await Promise.all([fetch(urlR1), fetch(urlR2)]);
    const [data1, data2] = await Promise.all([res1.json(), res2.json()]);

    if (data1.routes && data1.routes[0]) {
      const coords1 = data1.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
      state.routeData.r1 = { distance: data1.routes[0].distance, duration: data1.routes[0].duration, coords: coords1 };
      if (polyR1Corp) { mapCorp.removeLayer(polyR1Corp); }
      if (polyR1Drv)  { mapDrv.removeLayer(polyR1Drv); }
      polyR1Corp = L.polyline(coords1, { color: '#10b981', weight: 5, opacity: 0.9 }).addTo(mapCorp);
      polyR1Drv  = L.polyline(coords1, { color: '#10b981', weight: 5, opacity: 0.9 }).addTo(mapDrv);
    }

    if (data2.routes && data2.routes[0]) {
      const coords2 = data2.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
      state.routeData.r2 = { distance: data2.routes[0].distance, duration: data2.routes[0].duration, coords: coords2 };
      polyR2Corp = L.polyline(coords2, { color: '#3b82f6', weight: 4, opacity: 0.5, dashArray: '8 6' });
      polyR2Drv  = L.polyline(coords2, { color: '#3b82f6', weight: 4, opacity: 0.5, dashArray: '8 6' });
    }

    updateMetrics();
  } catch (e) {
    console.warn('OSRM offline — using embedded road-centerline fallback:', e.message);
    // Graceful fallback: use the static 27-point route already drawn
    updateMetrics();
  }
}

// ── ROUTE SELECTION TOGGLE ────────────────────────────────────────
function selectRoute(n) {
  state.activeRoute = n;

  // Toggle button styles
  document.getElementById('btn-r1').className = 'route-btn' + (n === 1 ? ' active-r1' : '');
  document.getElementById('btn-r2').className = 'route-btn' + (n === 2 ? ' active-r2' : '');

  // Show/hide polylines
  [polyR1Corp, polyR1Drv, polyR2Corp, polyR2Drv].forEach(p => p && p.remove());

  if (n === 1) {
    if (polyR1Corp) polyR1Corp.addTo(mapCorp);
    if (polyR1Drv)  polyR1Drv.addTo(mapDrv);
    if (polyR2Corp) { polyR2Corp.setStyle({ opacity: 0.2 }); polyR2Corp.addTo(mapCorp); }
    if (polyR2Drv)  { polyR2Drv.setStyle({ opacity: 0.2 }); polyR2Drv.addTo(mapDrv); }
  } else {
    if (polyR2Corp) { polyR2Corp.setStyle({ color:'#3b82f6', weight:5, opacity:0.9, dashArray:'' }); polyR2Corp.addTo(mapCorp); }
    if (polyR2Drv)  { polyR2Drv.setStyle({ color:'#3b82f6', weight:5, opacity:0.9, dashArray:'' }); polyR2Drv.addTo(mapDrv); }
    if (polyR1Corp) { polyR1Corp.setStyle({ opacity: 0.2 }); polyR1Corp.addTo(mapCorp); }
    if (polyR1Drv)  { polyR1Drv.setStyle({ opacity: 0.2 }); polyR1Drv.addTo(mapDrv); }
  }

  updateMetrics();
}

// ── SIMULATION CONTROLS ───────────────────────────────────────────
function updateProgress(val) {
  state.progressPct = parseInt(val);
  document.getElementById('progress-val').textContent = val + '%';
  updateMetrics();
}

function toggleWeather() {
  state.weather = state.weather === 'Rain' ? 'Clear' : 'Rain';
  const btn = document.getElementById('btn-weather');
  btn.textContent = state.weather === 'Rain' ? '🌧 Rain' : '☀️ Clear';
  btn.style.color = state.weather === 'Rain' ? 'var(--blue)' : 'var(--em-lt)';
  updateMetrics();
}

function toggleTime() {
  state.time = state.time === 'Night' ? 'Day' : 'Night';
  const btn = document.getElementById('btn-time');
  btn.textContent = state.time === 'Night' ? '🌙 Night' : '☀️ Day';
  updateMetrics();
}

function setCargo(val) { state.cargo = val; updateMetrics(); }
function setLang(val)  { state.lang = val; updateMetrics(); renderChat(); }

// ── SMART NLP ENGINE with Language Fallback Chain ─────────────────
function safeGetReply(replyObj, lang) {
  // Fallback chain: requested lang → Urdu → English → first available
  try {
    if (replyObj[lang])    return replyObj[lang];
    if (replyObj['Urdu'])  return replyObj['Urdu'];
    if (replyObj['English']) return replyObj['English'];
    const keys = Object.keys(replyObj);
    if (keys.length > 0)   return replyObj[keys[0]];
    return '📡 IDAS: Message received. Dispatch monitoring.';
  } catch (e) {
    return '📡 IDAS: Network reconnecting… Please try again.';
  }
}

function generateSmartReply(userText) {
  const val  = (userText || '').toLowerCase().trim();
  const lang = state.lang;

  const route = state.routeData['r' + state.activeRoute];
  const totalKm = route ? parseFloat((route.distance / 1000).toFixed(1)) : 162.5;
  const covered = parseFloat((totalKm * state.progressPct / 100).toFixed(1));
  const remKm   = parseFloat((totalKm - covered).toFixed(1));

  let avgSpeed = 65;
  if (state.weather === 'Rain' && state.time === 'Night') avgSpeed = 42;
  else if (state.weather === 'Rain' || state.time === 'Night') avgSpeed = 55;

  const remMin = Math.round((remKm / avgSpeed) * 60);
  const hrs    = Math.floor(remMin / 60);
  const mins   = remMin % 60;
  const spd    = avgSpeed + ' km/h';
  const fuelLeft = fmtCost(calcFuelCost(remKm));

  // Intent matching
  if (/route|rasto|raah|give|where|path|map|destination|way|kahan|location|mera rasta|raasta/i.test(val)) {
    return {
      English: `🗺️ ROUTE DISPATCH [Route ${state.activeRoute}]: Active corridor Mithi → Hyderabad (${totalKm} km). Covered: ${covered} km near Digri. Remaining: ${remKm} km. ETA: ${hrs}h ${mins}m.`,
      Sindhi:  `🗺️ RASTO DISPATCH [Route ${state.activeRoute}]: Tuhajo rasto Mithi → Hyderabad (${totalKm} km). ${covered} km puras near Digri. ${remKm} km baaki. ETA: ${hrs} kalak ${mins} min.`,
      Urdu:    `🗺️ RASTA DISPATCH [Route ${state.activeRoute}]: Rasta Mithi → Hyderabad (${totalKm} km). ${covered} km Digri ke paas mukammal. ${remKm} km baaqi. ETA: ${hrs} ghante ${mins} min.`,
      Dhatki:  `🗺️ RAAH DISPATCH [Route ${state.activeRoute}]: Taaro raah Mithi → Hyderabad (${totalKm} km). ${covered} km Digri paas pura. ${remKm} km baaki. ETA: ${hrs} kalak ${mins} min.`
    };
  }
  if (/mura|muri|mor|side|direction|kayi|turn|left|right|wanjo|khabbe|saje|modh/i.test(val)) {
    return {
      English: `🧭 DIRECTION ADVISORY: Straight ahead on National Highway 8 for next 45 km. No turn required at Naukot junction — stay on NH-8 toward Matli.`,
      Sindhi:  `🧭 DIRECTION ADVISORY: National Highway 8 te siddho vanj 45 km tak. Naukot junction te seedha — NH-8 te rehvo Matli taraf.`,
      Urdu:    `🧭 DIRECTION ADVISORY: Agle 45 km seedha National Highway 8 par chalein. Naukot junction par seedhe rahein — Matli ki taraf NH-8 par.`,
      Dhatki:  `🧭 DIRECTION ADVISORY: National Highway 8 te siddha vanj 45 km. Naukot junction te seedha — Matli vaaro NH-8 te raho.`
    };
  }
  if (/speed|fast|slow|raftar|tez|limit|chalo|raftaar/i.test(val)) {
    return {
      English: `⚡ SPEED ADVISORY: Recommended speed ${spd} — ${state.weather} weather, ${state.time} conditions. Maintain 6-second gap from vehicle ahead. No overtaking on wet road.`,
      Sindhi:  `⚡ RAFTAR ADVISORY: Recommended raftar ${spd} — ${state.weather} mosam, ${state.time}. Aage wari gadi thon 6 second doori rakho. Giili sadak te overtake na kayo.`,
      Urdu:    `⚡ RAFTAR ADVISORY: Tajweez karda raftaar ${spd} — ${state.weather} mausam, ${state.time}. Aage wali gadi se 6 second ka fasla rakhein. Geeli sadak par overtake mat karein.`,
      Dhatki:  `⚡ RAFTAR ADVISORY: Recommended raftar ${spd} — ${state.weather} mosam, ${state.time}. Agiy gaadi thon 6 second doori rakhna. Giili raah te overtake na karo.`
    };
  }
  if (/time|eta|distance|km|duration|pohchan|wqt|ghante|when|reach|kitna|pahuncho/i.test(val)) {
    return {
      English: `⏱️ ETA DISPATCH: ${hrs}h ${mins}m remaining to Hyderabad. Distance left: ${remKm} km. Estimated fuel remaining: ${fuelLeft}. Maintain ${spd} for on-time arrival.`,
      Sindhi:  `⏱️ ETA DISPATCH: Hyderabad pohchan mein ${hrs} kalak ${mins} min baaki. ${remKm} km baaki. Fuel: ${fuelLeft}. ${spd} raftar rakho waqt te pohchan laye.`,
      Urdu:    `⏱️ ETA DISPATCH: Hyderabad pahunche mein ${hrs} ghante ${mins} min baaqi. ${remKm} km baaqi. Fuel: ${fuelLeft}. Waqt par pahunche ke liye ${spd} raftaar rakhein.`,
      Dhatki:  `⏱️ ETA DISPATCH: Hyderabad ppohche mein ${hrs} kalak ${mins} min baaki. ${remKm} km baaki. Fuel: ${fuelLeft}.`
    };
  }
  if (/maal|tamatar|cargo|load|gadi|tomato|produce|fragile|pyaz|onion|cotton|wheat/i.test(val)) {
    return {
      English: `🍅 CARGO ADVISORY: Active cargo: ${state.cargo}. Cargo temperature: 19.2°C ✅. Avoid speed above ${spd}. No sudden braking — maintain 8-second deceleration distance.`,
      Sindhi:  `🍅 MAAL ADVISORY: Gadi mein ${state.cargo}. Temp: 19.2°C ✅. ${spd} thon tez na vanj. Achanak brake na kayo — 8 second dhimi karo.`,
      Urdu:    `🍅 MAAL ADVISORY: Gadi mein ${state.cargo}. Temp: 19.2°C ✅. ${spd} se tez mat chalein. Achanak brake mat lagayein — 8 second mein dhire karein.`,
      Dhatki:  `🍅 MAAL ADVISORY: Gadi mein ${state.cargo}. Temp: 19.2°C ✅. Achanak brake na karo.`
    };
  }
  if (/fuel|petrol|gas|pump|cost|price|kharcha|paisa|rupay/i.test(val)) {
    const totalFuel = fmtCost(calcFuelCost(totalKm));
    return {
      English: `⛽ FUEL DISPATCH: Total route fuel cost: ${totalFuel} (${totalKm} km ÷ 8 km/L × Rs.282). Remaining fuel cost: ${fuelLeft}. Next fuel station: Naukot (~18 km ahead).`,
      Sindhi:  `⛽ PETROL INFO: Total safar kharcha: ${totalFuel}. Baaki kharcha: ${fuelLeft}. Aglo pump: Naukot (~18 km aage).`,
      Urdu:    `⛽ PETROL INFO: Poore safar ka kharcha: ${totalFuel}. Baaki kharcha: ${fuelLeft}. Agla pump: Naukot (~18 km aage).`,
      Dhatki:  `⛽ PETROL INFO: Total kharcha: ${totalFuel}. Baaki: ${fuelLeft}. Aglo pump: Naukot (~18 km).`
    };
  }
  if (/weather|rain|barish|mosam|night|raat|dark|slippery|chikni/i.test(val)) {
    return {
      English: `🌧️ WEATHER ALERT: Current: ${state.weather}, ${state.time}. Road friction μ=0.38 (Wet). Stopping distance increased 2×. Keep hazard lights ON. Avoid overtaking.`,
      Sindhi:  `🌧️ MOSAM ALERT: Maujuda: ${state.weather}, ${state.time}. Sadak chikani ahe (μ=0.38). Rukan wari doori 2× wadi ahe. Hazard lights on rakho.`,
      Urdu:    `🌧️ MAUSAM ALERT: Maujuda: ${state.weather}, ${state.time}. Sadak phislan wali (μ=0.38). Rokne ki doori 2× barh gayi. Hazard lights on rakhein.`,
      Dhatki:  `🌧️ MOSAM ALERT: Maujuda: ${state.weather}, ${state.time}. Sadak chikani hai. Hazard lights on rakho.`
    };
  }
  if (/hello|hi|salam|aayo|kiin|kean|welcome|khush|assalam/i.test(val)) {
    return {
      English: `👋 IDAS DISPATCH: Welcome TRK-119! Route ${state.activeRoute} active — Mithi → Hyderabad (${state.progressPct}% complete). Weather: ${state.weather}. How can dispatch assist?`,
      Sindhi:  `👋 IDAS DISPATCH: Khush aayo TRK-119! Route ${state.activeRoute} active — ${state.progressPct}% mukammal. Mosam: ${state.weather}. Kihn madad kayo?`,
      Urdu:    `👋 IDAS DISPATCH: Khush aamdeed TRK-119! Route ${state.activeRoute} active — ${state.progressPct}% mukammal. Mausam: ${state.weather}. Kaise madad karein?`,
      Dhatki:  `👋 IDAS DISPATCH: Aavkaari TRK-119! Route ${state.activeRoute} — ${state.progressPct}% mukammal. Kihn madad karo?`
    };
  }
  if (/kharab|breakdown|help|madad|emergency|accident|jam|janwar|hazard|khatro|stuck/i.test(val)) {
    return {
      English: `🚨 HIGH-PRIORITY ALERT: Hazard logged at ${covered} km mark (TRK-119). Alternate route via Diplo being computed. Nearest assistance: Naukot Police Post (~12 km). Stay calm.`,
      Sindhi:  `🚨 HIGH-PRIORITY ALERT: TRK-119 ${covered} km wath khatro register thia. Diplo rasto nayo alert. Naukot Police Post (~12 km). Saabit raho.`,
      Urdu:    `🚨 HIGH-PRIORITY ALERT: TRK-119 ${covered} km par hazard register. Diplo se alternate rasta. Naukot Police Post (~12 km). Saabit rahein.`,
      Dhatki:  `🚨 HIGH-PRIORITY ALERT: TRK-119 ${covered} km paas khatro. Diplo waaro nayo raah. Naukot Police Post (~12 km). Saabit raho.`
    };
  }
  if (/route 1|route 2|fastest|shortest|badlo|change route|swap/i.test(val)) {
    const next = state.activeRoute === 1 ? 2 : 1;
    selectRoute(next);
    return {
      English: `🔄 ROUTE CHANGED: Switched to Route ${next} (${next === 1 ? 'Fastest' : 'Shortest Distance'}). Recalculating ETA and fuel cost…`,
      Sindhi:  `🔄 RASTO BADLIYO: Route ${next} (${next === 1 ? 'Tez' : 'Ghat Km'}) te ayo. ETA aur fuel recalculate aahin…`,
      Urdu:    `🔄 RASTA BADLA: Route ${next} (${next === 1 ? 'Sabse Tez' : 'Sabse Chhota'}) par aa gaye. ETA aur fuel recalculate ho raha hai…`,
      Dhatki:  `🔄 RAAH BADLIYO: Route ${next} te aayo. ETA aur fuel hisaab aahin…`
    };
  }

  // ── Dynamic Context-Aware Fallback ─────────────────────────────
  return {
    English: `📡 DISPATCH ASSISTANT: Message logged for TRK-119. Active: Route ${state.activeRoute} — ${covered} km of ${totalKm} km (${state.progressPct}%). Speed: ${spd}. ETA: ${hrs}h ${mins}m. Fuel left: ${fuelLeft}.`,
    Sindhi:  `📡 DISPATCH ASSISTANT: TRK-119 paighaam record thia. Route ${state.activeRoute} — ${covered} km puras ${totalKm} km mein (${state.progressPct}%). Raftar: ${spd}. ETA: ${hrs}h ${mins}m. Fuel: ${fuelLeft}.`,
    Urdu:    `📡 DISPATCH ASSISTANT: TRK-119 paigham record. Route ${state.activeRoute} — ${covered} km mukamal ${totalKm} km mein (${state.progressPct}%). Raftar: ${spd}. ETA: ${hrs}h ${mins}m. Fuel: ${fuelLeft}.`,
    Dhatki:  `📡 DISPATCH ASSISTANT: TRK-119 sandesh record. Route ${state.activeRoute} — ${covered} km pura (${state.progressPct}%). Raftar: ${spd}. ETA: ${hrs}h ${mins}m.`
  };
}

// ── CHAT RENDER ───────────────────────────────────────────────────
function renderChat() {
  const corpBox = document.getElementById('corp-chat-box');
  const drvBox  = document.getElementById('drv-chat-box');
  let hCorp = '', hDrv = '';

  state.messages.forEach(msg => {
    const isDrv  = msg.role === 'driver';
    const engTxt = isDrv ? msg.original : msg.english;
    const drvTxt = isDrv ? msg.original : safeGetReply(msg.replyObj || {}, state.lang);

    hCorp += `<div class="chat-row ${isDrv ? 'driver' : 'corporate'}">
      <div class="chat-avatar">${isDrv ? '🚚' : '🏢'}</div>
      <div>
        <div class="chat-bubble">${engTxt}</div>
        <div class="chat-meta">${isDrv ? '🌐 ' + state.lang + ' → EN' : '🏢 Corporate EN'}</div>
      </div></div>`;

    hDrv += `<div class="chat-row ${isDrv ? 'driver' : 'corporate'}">
      <div class="chat-avatar">${isDrv ? '🚚' : '🏢'}</div>
      <div>
        <div class="chat-bubble">${drvTxt}</div>
        <div class="chat-meta">${isDrv ? 'You (' + state.lang + ')' : '🏢 → ' + state.lang}</div>
      </div></div>`;
  });

  corpBox.innerHTML = hCorp || '<div style="text-align:center;color:var(--text3);font-size:0.75rem;padding:20px;">No messages yet — dispatch awaiting contact.</div>';
  drvBox.innerHTML  = hDrv  || '<div style="text-align:center;color:var(--text3);font-size:0.75rem;padding:20px;">Chat in any language — Sindhi, Urdu, Dhatki, or English.</div>';
  corpBox.scrollTop = corpBox.scrollHeight;
  drvBox.scrollTop  = drvBox.scrollHeight;
}

// ── SEND DRIVER MESSAGE ───────────────────────────────────────────
function sendDrvMessage(e) {
  e.preventDefault();
  const inp = document.getElementById('drv-chat-input');
  const val = inp.value.trim();
  if (!val) return;

  const replyObj = generateSmartReply(val);
  const isHazard = /kharab|breakdown|help|madad|emergency|accident|hazard|khatro/i.test(val);

  state.messages.push({
    role: 'driver',
    original: isHazard ? '🚨 ' + val : val,
    english:  isHazard ? '🚨 HAZARD: ' + val : val
  });
  state.messages.push({
    role: 'corporate',
    english:  safeGetReply(replyObj, 'English'),
    replyObj: replyObj
  });

  inp.value = '';
  renderChat();
}

// ── SEND CORPORATE MESSAGE ────────────────────────────────────────
function sendCorpMessage(e) {
  e.preventDefault();
  const inp = document.getElementById('corp-chat-input');
  const val = inp.value.trim();
  if (!val) return;

  const response = {
    English: '✅ Advisory received by TRK-119. Driver notified in ' + state.lang + '.',
    Sindhi:  '✅ Dispatch advisory TRK-119 khe mili. Driver khe ' + state.lang + ' mein dassayo.',
    Urdu:    '✅ Dispatch advisory TRK-119 ko mili. Driver ko ' + state.lang + ' mein bataya gaya.',
    Dhatki:  '✅ Advisory TRK-119 khe mili. Driver khe ' + state.lang + ' mein dassayo.'
  };

  state.messages.push({ role: 'corporate', english: '🏢 DISPATCH: ' + val, replyObj: { English: '🏢 DISPATCH: ' + val, Sindhi: '🏢 DISPATCH: ' + val, Urdu: '🏢 DISPATCH: ' + val, Dhatki: '🏢 DISPATCH: ' + val } });
  state.messages.push({ role: 'driver', original: safeGetReply(response, state.lang), english: response.English });

  inp.value = '';
  renderChat();
}

// ── VOICE SYNTHESIS (language-aware) ─────────────────────────────
function speakAlert() {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();

  const langMap = { Sindhi: 'ur-PK', Urdu: 'ur-PK', Dhatki: 'ur-PK', English: 'en-US' };
  const msgs = {
    English: `IDAS Alert for Truck 119. ${state.weather} conditions on National Highway 8. Recommended speed ${document.getElementById('spd-display').textContent}. Drive safely.`,
    Sindhi:  `IDAS Alert TRK-119 laye. National Highway 8 te ${state.weather}. Raftar ${document.getElementById('spd-display').textContent}. Salaamti saan halo.`,
    Urdu:    `IDAS Alert Truck 119. National Highway 8 par ${state.weather}. Raftar ${document.getElementById('spd-display').textContent}. Salamti se chalein.`,
    Dhatki:  `IDAS Alert TRK-119. NH-8 te ${state.weather}. Raftar ${document.getElementById('spd-display').textContent}. Salaamti vanj.`
  };

  const utt = new SpeechSynthesisUtterance(msgs[state.lang] || msgs.English);
  utt.lang = langMap[state.lang] || 'en-US';
  utt.rate = 0.88;
  utt.pitch = 1.0;
  window.speechSynthesis.speak(utt);
}

// ── INITIAL WELCOME MESSAGE ───────────────────────────────────────
function initWelcomeMessages() {
  const replyObj = {
    English: '🌾 Agri-IDAS v3.0 online. TRK-119 connected on Mithi → Hyderabad corridor. Dual route options loaded. Type any question in any language.',
    Sindhi:  '🌾 Agri-IDAS v3.0 online. TRK-119 Mithi → Hyderabad raste te connect thio. Do route options load thia. Koi bhi sawaal pucho kisi bhi zaban mein.',
    Urdu:    '🌾 Agri-IDAS v3.0 online. TRK-119 Mithi → Hyderabad raste par connect ho gaya. Do route options load ho gaye. Kisi bhi zaban mein sawal karein.',
    Dhatki:  '🌾 Agri-IDAS v3.0 online. TRK-119 Mithi → Hyderabad raah te connect thio. Do route options load thia.'
  };
  state.messages.push({ role: 'corporate', english: replyObj.English, replyObj: replyObj });
  renderChat();
}

// ── BOOT ──────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initMaps();
  initWelcomeMessages();
  updateMetrics();
});

// Map resize on orientation change
window.addEventListener('resize', () => {
  setTimeout(() => {
    if (mapCorp) mapCorp.invalidateSize();
    if (mapDrv)  mapDrv.invalidateSize();
  }, 200);
});
</script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'SUCCESS — index.html written: {len(html):,} bytes, {html.count(chr(10))} lines')
