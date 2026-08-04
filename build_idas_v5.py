"""
build_idas_v5.py — Uses Leaflet Routing Machine (LRM) for 100% road-aligned routing.
LRM calls OSRM internally and renders routes PERFECTLY on road centerlines.
No pre-embedded coordinates needed — the plugin handles it all automatically.
"""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agri-Logistics IDAS · Phase 3 Research Portal</title>
<meta name="description" content="Agri-IDAS — Trilingual AI logistics dispatch for Sindh agricultural transport. True-road GIS routing, NLP chatbot, IoT telemetry.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<!-- Leaflet Routing Machine CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.css"/>
<style>
/* ─── HIDE LRM CONTROL PANEL (we only want the line) ──── */
.leaflet-routing-container,
.leaflet-routing-container-hide,
.leaflet-routing-geocoders { display: none !important; }

/* ─── DESIGN TOKENS ──────────────────────────────────── */
:root {
  --bg:         #F5F2EC;
  --primary:    #2D5016;
  --primary-dk: #1E3A0F;
  --primary-lt: #4A7C2F;
  --gold:       #D4AF37;
  --card-bg:    #FFFFFF;
  --text-dk:    #2D3A1F;
  --text-muted: #5C6B4A;
  --border:     #EAE6DE;
  --blue:       #1D4ED8;
  --blue-lt:    #3B82F6;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: "Inter", sans-serif; background: var(--bg); color: var(--text-dk); line-height: 1.5; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #c4bdb0; border-radius: 3px; }

/* ─── LAYOUT ─────────────────────────────────────────── */
.app-layout { display: flex; min-height: 100vh; }
.sidebar {
  width: 300px; flex-shrink: 0;
  background: linear-gradient(180deg,#111A06 0%,#1E2E0A 60%,#2A3F10 100%);
  border-right: 1px solid #3A5215;
  padding: 22px 18px; color: #D0DEB8; overflow-y: auto;
}
.main-content { flex: 1; padding: 28px 32px; overflow-y: auto; }

@media(max-width:900px) {
  .app-layout { flex-direction: column; }
  .sidebar { width: 100%; }
  .grid-2 { grid-template-columns: 1fr !important; }
  .grid-kpi { grid-template-columns: repeat(2,1fr) !important; }
  .controls-row { grid-template-columns: repeat(2,1fr) !important; }
}

/* ─── SIDEBAR ────────────────────────────────────────── */
.academic-card {
  background: linear-gradient(160deg,#1A2409,#243310);
  border: 1px solid #5A4A1A; border-left: 4px solid var(--gold);
  border-radius: 14px; padding: 18px; margin-bottom: 18px;
}
.ac-badge {
  background: var(--gold); color: #1A1000;
  font-size: 0.63rem; font-weight: 800;
  padding: 3px 10px; border-radius: 20px;
  letter-spacing: 1px; text-transform: uppercase;
  display: inline-block; margin-bottom: 10px;
}
.ac-name { color:#FFF; font-size:1.1rem; font-weight:800; margin-bottom:2px; }
.ac-id   { color:var(--gold); font-size:0.76rem; font-weight:600; }
.ac-divider { border:none; border-top:1px solid #3A4F1A; margin:10px 0; }
.ac-row { font-size:0.73rem; margin-bottom:7px; color:#D0DEB8; }

.sidebar-section {
  background:#1A2409; border-radius:10px;
  padding:14px; margin-bottom:14px;
  font-size:0.73rem; line-height:1.7;
}
.sidebar-section h4 {
  color:#C8D8A0; font-size:0.76rem; text-transform:uppercase;
  letter-spacing:.8px; margin-bottom:8px;
  border-bottom:1px solid #2D4012; padding-bottom:4px;
}

.route-section { background:#1A2409; border-radius:10px; padding:14px; margin-bottom:14px; }
.route-section h4 { color:#C8D8A0; font-size:0.76rem; text-transform:uppercase; letter-spacing:.8px; margin-bottom:10px; border-bottom:1px solid #2D4012; padding-bottom:4px; }
.route-opt {
  display:flex; align-items:center; gap:10px;
  padding:10px 12px; border-radius:8px;
  border:1px solid #3A5215; background:#111A06;
  cursor:pointer; transition:all 0.2s; margin-bottom:8px;
}
.route-opt.active { background:#1E3A0F; border-color:var(--primary-lt); }
.rdot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.rdot.r1 { background:#4A7C2F; }
.rdot.r2 { background:var(--blue-lt); }
.route-opt-lbl  { font-size:0.75rem; color:#C8D8A0; font-weight:600; }
.route-opt-meta { font-size:0.67rem; color:#7A9A60; margin-top:2px; }

.fuel-card {
  background:linear-gradient(135deg,#1A2409,#243310);
  border:1px solid #5A4A1A; border-left:4px solid var(--gold);
  border-radius:10px; padding:12px; margin-bottom:14px;
}
.fuel-lbl { color:#A0B880; font-size:0.67rem; text-transform:uppercase; letter-spacing:.8px; margin-bottom:3px; }
.fuel-val { color:var(--gold); font-size:1.3rem; font-weight:800; }
.fuel-note { color:#7A9A60; font-size:0.67rem; margin-top:3px; }

/* ─── HEADER ─────────────────────────────────────────── */
.app-header {
  background:linear-gradient(135deg,#1E3A0F 0%,#2D5016 50%,#3D6B22 100%);
  border-radius:14px; padding:20px 28px; margin-bottom:22px;
  display:flex; align-items:center; justify-content:space-between;
  box-shadow:0 4px 20px rgba(45,80,22,.25); color:#FFF;
}
.app-header h1 { font-size:1.55rem; font-weight:800; letter-spacing:-.5px; }
.app-header p  { color:#C5DFA0; font-size:0.8rem; margin-top:3px; }
.header-badge {
  background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.3);
  color:#FFF; font-size:0.68rem; font-weight:700;
  padding:4px 12px; border-radius:20px; letter-spacing:.8px;
}

/* ─── TAB BAR ────────────────────────────────────────── */
.tab-bar {
  display:flex; gap:10px; background:#E2DDD0;
  border-radius:12px; padding:6px; border:1px solid #C4BDAC;
  margin-bottom:22px;
}
.tab-btn {
  flex:1; padding:11px 20px; border-radius:8px;
  border:1px solid var(--primary-dk);
  background:var(--primary); color:#FFF;
  font-weight:700; font-size:0.88rem; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:8px;
  transition:all 0.2s;
}
.tab-btn.active {
  background:#FFF !important; color:var(--primary-dk) !important;
  border:2px solid var(--primary) !important;
  box-shadow:0 4px 14px rgba(0,0,0,.15);
}

/* ─── GRID & CARDS ───────────────────────────────────── */
.grid-2   { display:grid; grid-template-columns:1.55fr 1fr; gap:22px; margin-bottom:22px; }
.grid-kpi { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:22px; }
.card {
  background:var(--card-bg); border-radius:14px;
  padding:20px 22px; box-shadow:0 2px 12px rgba(0,0,0,.06);
  border:1px solid var(--border);
}
.card h4 { font-size:0.93rem; font-weight:700; color:var(--primary-dk); margin-bottom:14px; display:flex; align-items:center; gap:8px; }
.metric-card { border-left:5px solid var(--primary-lt); }
.metric-card h3 { font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:.8px; }
.metric-value { font-size:1.75rem; font-weight:800; color:var(--primary-dk); margin:4px 0; }
.metric-delta { font-size:0.73rem; font-weight:600; }

/* ─── SAFETY ALERT ───────────────────────────────────── */
@keyframes slide-in { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
.safety-alert {
  border-radius:12px; padding:16px 18px; margin-bottom:18px;
  display:flex; align-items:flex-start; gap:14px;
  border-left:5px solid; box-shadow:0 2px 10px rgba(0,0,0,.07);
  animation:slide-in 0.35s ease;
}
.safety-alert.standard { background:#E8F4FD; border-color:#2196F3; color:#0C4375; }
.safety-alert.warning  { background:#FFF4E5; border-color:#FF9800; color:#6B3800; }
.safety-alert.critical { background:#FDECEA; border-color:#F44336; color:#6A1911; }
.safety-alert.extreme  { background:#1A0505; border-color:#FF0000; color:#FFD0CC; }
.safety-icon { font-size:1.75rem; line-height:1; }
.safety-text h5 { font-size:0.9rem; font-weight:800; margin-bottom:3px; }
.safety-text p  { font-size:0.8rem; line-height:1.5; }

/* ─── MAP ────────────────────────────────────────────── */
.map-container { height:300px; border-radius:10px; overflow:hidden; border:1px solid #D0C9B8; position:relative; }
.map-status-bar {
  position:absolute; bottom:6px; left:6px; z-index:500;
  background:rgba(30,58,15,.88); color:#C5DFA0;
  font-size:0.65rem; font-weight:700; padding:4px 10px;
  border-radius:20px; letter-spacing:.5px;
  pointer-events:none;
}

/* ─── CHAT ───────────────────────────────────────────── */
.chat-box {
  height:230px; overflow-y:auto; padding:12px;
  background:#FAFAF8; border-radius:10px;
  border:1px solid var(--border); margin-bottom:10px;
  display:flex; flex-direction:column; gap:10px;
}
.chat-row { display:flex; gap:8px; align-items:flex-end; }
.chat-row.driver { flex-direction:row-reverse; }
.chat-avatar {
  width:28px; height:28px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:0.8rem; flex-shrink:0; background:#EAE6DE;
}
.chat-row.driver .chat-avatar { background:var(--primary); }
.chat-bubble {
  padding:8px 12px; border-radius:14px;
  font-size:0.82rem; line-height:1.5; max-width:82%;
}
.chat-row.corporate .chat-bubble { background:#EDEBE4; color:#2D3A1F; border-bottom-left-radius:4px; }
.chat-row.driver    .chat-bubble { background:var(--primary); color:#FFF; border-bottom-right-radius:4px; }
.chat-meta { font-size:0.62rem; color:#A09880; margin-top:2px; }
.chat-input-row { display:flex; gap:8px; }
.chat-input-row input {
  flex:1; padding:9px 13px; border-radius:8px;
  border:1px solid #C4BDAC; font-size:0.84rem; outline:none;
  font-family:"Inter",sans-serif; transition:border-color 0.2s;
}
.chat-input-row input:focus { border-color:var(--primary-lt); }
.chat-input-row button {
  padding:9px 16px; border-radius:8px; border:none;
  background:var(--primary-dk); color:#FFF;
  font-weight:700; cursor:pointer; transition:background 0.2s;
  white-space:nowrap;
}
.chat-input-row button:hover { background:var(--primary); }

/* ─── PROGRESS BAR ───────────────────────────────────── */
.prog-track { background:#EAE6DE; border-radius:10px; height:10px; overflow:hidden; margin-bottom:10px; }
.prog-fill  { background:linear-gradient(90deg,#4A7C2F,#2D5016); height:100%; transition:width .3s ease; }

/* ─── CONTROLS ───────────────────────────────────────── */
.controls-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }
.control-group label { display:block; font-size:0.77rem; font-weight:700; color:var(--primary-dk); margin-bottom:4px; }
.control-group select {
  width:100%; padding:8px 10px; border-radius:8px;
  border:1px solid #C4BDAC; font-weight:600; color:var(--primary-dk);
  outline:none; font-family:"Inter",sans-serif;
}

/* ─── TELEMETRY ──────────────────────────────────────── */
.tele-row { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F0EDE6; font-size:0.81rem; }
.tele-label { color:var(--text-muted); font-weight:600; }
.tele-val   { color:var(--primary-dk); font-weight:700; }

/* ─── AUDIO ──────────────────────────────────────────── */
.audio-box { background:#F0EDE6; padding:12px; border-radius:8px; border-left:3px solid var(--primary-lt); font-size:0.81rem; margin-bottom:12px; }
.play-btn { width:100%; padding:10px; border-radius:8px; border:none; background:var(--primary); color:#FFF; font-weight:700; cursor:pointer; }
.play-btn:hover { background:var(--primary-dk); }

/* ─── FOOTER ─────────────────────────────────────────── */
.ieee-footer {
  background:linear-gradient(135deg,#111A06,#1E2E0A);
  border-radius:14px; padding:18px 26px; margin-top:28px;
  color:#A0B880; font-size:0.71rem;
  display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;
}
.footer-title { color:var(--gold); font-weight:700; margin-bottom:4px; }
</style>
</head>
<body>
<div class="app-layout">

<!-- ══════════════════════════════════
     SIDEBAR
════════════════════════════════════ -->
<aside class="sidebar">
  <div class="academic-card">
    <span class="ac-badge">🎓 Research Author</span>
    <h3 class="ac-name">Lokesh Kumar</h3>
    <p class="ac-id">Student ID: 2k22-SE-42</p>
    <hr class="ac-divider">
    <div class="ac-row">📧 2K22-SE-42@student.sau.edu.pk</div>
    <div class="ac-row">🏫 Sindh Agriculture University, Tandojam</div>
    <div class="ac-row">📄 Dept. of Software Engineering</div>
    <div class="ac-row" style="margin-top:8px;border-top:1px dashed #3A4F1A;padding-top:8px;color:var(--gold);">
      ⭐ Supervision:<br>Prof. Dr. Bhawani Shankar Chowdhry
    </div>
  </div>

  <!-- Route Selection -->
  <div class="route-section">
    <h4>🛣️ Route Selection</h4>
    <div class="route-opt active" id="r1-opt" onclick="selectRoute(1)">
      <span class="rdot r1"></span>
      <div>
        <div class="route-opt-lbl">Route 1 — Fastest</div>
        <div class="route-opt-meta" id="r1-meta">Calculating…</div>
      </div>
    </div>
    <div class="route-opt" id="r2-opt" onclick="selectRoute(2)">
      <span class="rdot r2"></span>
      <div>
        <div class="route-opt-lbl">Route 2 — Via Naukot</div>
        <div class="route-opt-meta" id="r2-meta">Calculating…</div>
      </div>
    </div>
  </div>

  <!-- Fuel Cost -->
  <div class="fuel-card">
    <div class="fuel-lbl">⛽ Estimated Fuel Cost</div>
    <div class="fuel-val" id="sb-fuel">Rs. 5,718</div>
    <div class="fuel-note">@ Rs.282/L · 8 km/L · <span id="sb-dist">162.5</span> km</div>
  </div>

  <!-- Research Info -->
  <div class="sidebar-section">
    <h4>📋 Research Context</h4>
    <strong style="color:#C8D8A0;">Title:</strong><br>
    <em>Bridging the Digital Literacy Gap in Rural Agri-Logistics Using a Trilingual, Context-Aware IDAS</em><br><br>
    <strong style="color:#C8D8A0;">Objective:</strong><br>
    Zero-literacy-barrier access to route safety for Sindhi, Urdu, and Dhatki drivers.
  </div>

  <div class="sidebar-section">
    <h4>⚙️ System Pipeline</h4>
    • Leaflet Routing Machine (LRM)<br>
    • OSRM True-Road Alignment<br>
    • Dual Route: Fastest &amp; Via Naukot<br>
    • 4-Tier Context-Aware Safety Matrix<br>
    • Trilingual NLP (Sindhi/Urdu/Dhatki)<br>
    • gTTS Audio &amp; IoT Telemetry
  </div>
</aside>

<!-- ══════════════════════════════════
     MAIN CONTENT
════════════════════════════════════ -->
<main class="main-content">

  <header class="app-header">
    <div>
      <h1>🌾 Agri-Logistics IDAS</h1>
      <p>Intelligent Driver Assistance System · Sindh Agricultural Supply Chain (Mithi → Hyderabad)</p>
    </div>
    <div style="text-align:right;">
      <span class="header-badge">PHASE 3 · FULL SYSTEM</span>
      <p style="font-size:0.7rem;color:var(--gold);margin-top:4px;">🌐 agri-idas.tech</p>
    </div>
  </header>

  <div class="tab-bar">
    <button class="tab-btn active" id="tab-corp-btn" onclick="switchTab('corp')">🏢 Corporate Dashboard</button>
    <button class="tab-btn"        id="tab-drv-btn"  onclick="switchTab('drv')">🚚 Driver Interface</button>
  </div>

  <!-- ══ CORPORATE TAB ══════════════════ -->
  <div id="tab-corp">
    <div class="grid-kpi">
      <div class="card metric-card">
        <h3>Route Distance</h3>
        <div class="metric-value" id="kpi-dist">—</div>
        <div class="metric-delta" id="kpi-dist-d" style="color:var(--primary-lt);">📍 Calculating…</div>
      </div>
      <div class="card metric-card">
        <h3>ETA Remaining</h3>
        <div class="metric-value" id="kpi-eta">—</div>
        <div class="metric-delta" id="kpi-eta-d" style="color:var(--primary-lt);">▼ On Schedule</div>
      </div>
      <div class="card metric-card">
        <h3>Fuel Cost (PKR)</h3>
        <div class="metric-value" id="kpi-fuel">—</div>
        <div class="metric-delta" style="color:var(--text-muted);">@ Rs.282/L · 8 km/L</div>
      </div>
      <div class="card metric-card" style="border-left-color:#C62828;">
        <h3>Safety Score</h3>
        <div class="metric-value" id="kpi-safety" style="color:#C62828;">48%</div>
        <div class="metric-delta" id="kpi-safety-d" style="color:#C62828;">▼ Rain + Night Risk</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <h4>🗺️ Live Fleet Map — Corporate View</h4>
        <div class="map-container">
          <div id="map-corp" style="width:100%;height:100%;"></div>
          <div class="map-status-bar" id="corp-status">⟳ Loading road-aligned route…</div>
        </div>
      </div>
      <div class="card">
        <h4>💬 Dispatch Chat (English View)</h4>
        <div class="chat-box" id="corp-chat-box"></div>
        <form class="chat-input-row" onsubmit="sendCorpMessage(event)">
          <input type="text" id="corp-chat-input" placeholder="Message TRK-119 driver (English)…" autocomplete="off">
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  </div>

  <!-- ══ DRIVER TAB ════════════════════ -->
  <div id="tab-drv" style="display:none;">
    <div class="controls-row">
      <div class="control-group">
        <label>🌐 Language</label>
        <select id="sel-lang" onchange="onCtrlChange()">
          <option value="Sindhi" selected>🌟 Sindhi</option>
          <option value="Urdu">🌙 Urdu</option>
          <option value="Dhatki">🌺 Dhatki</option>
          <option value="English">🌐 English</option>
        </select>
      </div>
      <div class="control-group">
        <label>📦 Cargo Type</label>
        <select id="sel-cargo" onchange="onCtrlChange()">
          <option value="Fragile" selected>🍅 Fragile / Tomatoes</option>
          <option value="Standard">📦 Standard</option>
          <option value="Cotton">🌿 Cotton</option>
          <option value="Wheat">🌾 Wheat</option>
        </select>
      </div>
      <div class="control-group">
        <label>⏱️ Time (Simulate)</label>
        <select id="sel-time" onchange="onCtrlChange()">
          <option value="Day">☀️ Day</option>
          <option value="Night" selected>🌙 Night</option>
        </select>
      </div>
      <div class="control-group">
        <label>☁️ Weather</label>
        <select id="sel-weather" onchange="onCtrlChange()">
          <option value="Clear">☀️ Clear</option>
          <option value="Rain" selected>🌧️ Rain</option>
        </select>
      </div>
    </div>

    <!-- Safety Alert -->
    <div id="safety-panel" class="safety-alert extreme">
      <div class="safety-icon" id="alert-icon">⛔</div>
      <div class="safety-text">
        <h5 id="alert-title">INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal</h5>
        <p id="alert-body">Teno khatarnak halat hik waqt gad thia aahin. Raftar 50% ghat karo. Hazard lights hinner chalao. Keh khe overtake na karo.</p>
      </div>
    </div>

    <!-- Route Progress -->
    <div class="card" style="margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <h4 style="margin:0;">🚗 Route Progress (Mithi → Hyderabad)</h4>
        <span id="prog-badge" style="background:#4A7C2F;color:#FFF;font-size:0.73rem;font-weight:700;padding:3px 10px;border-radius:12px;">35% Completed</span>
      </div>
      <div class="prog-track">
        <div class="prog-fill" id="prog-fill" style="width:35%;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:0.77rem;color:#4A5C3A;font-weight:600;margin-bottom:8px;">
        <span id="prog-covered">📍 Covered: — km</span>
        <span id="prog-eta">⏱️ ETA: Calculating…</span>
      </div>
      <input type="range" id="prog-slider" min="0" max="100" value="35"
        style="width:100%;accent-color:#4A7C2F;cursor:pointer;"
        oninput="updateProgress(this.value)">
    </div>

    <!-- Driver Map + Chat -->
    <div class="grid-2">
      <div class="card">
        <h4>🧭 Navigation View — Driver</h4>
        <div class="map-container">
          <div id="map-drv" style="width:100%;height:100%;"></div>
          <div class="map-status-bar" id="drv-status">⟳ Loading road-aligned route…</div>
        </div>
      </div>
      <div class="card">
        <h4 id="drv-chat-title">💬 Dispatch Chat (🌟 Sindhi)</h4>
        <div class="chat-box" id="drv-chat-box"></div>
        <form class="chat-input-row" onsubmit="sendDrvMessage(event)">
          <input type="text" id="drv-chat-input" placeholder="Type in any language…" autocomplete="off">
          <button type="submit">Send</button>
        </form>
      </div>
    </div>

    <!-- Audio + Telemetry -->
    <div class="grid-2">
      <div class="card">
        <h4>🔊 Audio Advisory Guidance</h4>
        <div class="audio-box">
          <strong>Next Maneuver:</strong> Continue on National Highway 8 toward Matli for 45 km.
        </div>
        <button class="play-btn" onclick="playAudio()">🔊 Play Advisory in Selected Language</button>
        <p id="audio-text" style="font-size:0.73rem;color:var(--text-muted);margin-top:8px;font-style:italic;"></p>
      </div>
      <div class="card">
        <h4>📡 IoT / WSN Vehicle Telemetry</h4>
        <div class="tele-row">
          <span class="tele-label">Current Speed</span>
          <span class="tele-val" id="tele-speed" style="color:#C62828;">42 km/h (Limit: 50)</span>
        </div>
        <div class="tele-row">
          <span class="tele-label">Road Surface</span>
          <span class="tele-val" id="tele-road">🌧️ Wet / Slippery (μ=0.38)</span>
        </div>
        <div class="tele-row">
          <span class="tele-label">Cargo Temp</span>
          <span class="tele-val" id="tele-cargo">19.2°C (Controlled)</span>
        </div>
        <div class="tele-row">
          <span class="tele-label">GPS Location</span>
          <span class="tele-val" id="tele-gps" style="font-family:monospace;font-size:0.76rem;">24.9729°N, 69.2927°E</span>
        </div>
        <div class="tele-row" style="border:none;">
          <span class="tele-label">WSN Gateway</span>
          <span class="tele-val" style="color:#2E7D32;">🟢 Active (4G + LoRaWAN)</span>
        </div>
      </div>
    </div>
  </div>

  <footer class="ieee-footer">
    <div>
      <div class="footer-title">📄 Research Citation</div>
      <em>Kumar, L.</em> (2024). "Bridging the Digital Literacy Gap in Rural Agri-Logistics." <em>Sindh Agriculture University Symposium.</em> Tandojam.
    </div>
    <div style="text-align:right;">
      Agri-Logistics IDAS · Phase 3<br>
      <strong style="color:var(--gold);">© 2024 Lokesh Kumar</strong>
    </div>
  </footer>
</main>
</div>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<!-- Leaflet Routing Machine — handles OSRM road-snapping automatically -->
<script src="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.min.js"></script>

<script>
'use strict';

// ── CONSTANTS ─────────────────────────────────────────────────────
const FUEL_PKR = 282, FUEL_EFF = 8;
const MITHI = L.latLng(24.7436, 69.7961);
const HYD   = L.latLng(25.3960, 68.3578);
// Via Naukot waypoint for Route 2
const NAUKOT = L.latLng(24.8450, 69.3800);

// ── STATE ─────────────────────────────────────────────────────────
const state = {
  lang:'Sindhi', cargo:'Fragile', time:'Night', weather:'Rain',
  progressPct:35, activeRoute:1,
  routeInfo:{ r1:null, r2:null },
  messages:[{
    role:'corporate',
    english:'🌾 Welcome TRK-119! Connected to IDAS Network. True-road routing active via Leaflet Routing Machine + OSRM. Safe travels on Mithi → Hyderabad corridor.'
  }]
};

// ── HELPERS ───────────────────────────────────────────────────────
const el = id => document.getElementById(id);
const fmtPKR = n => 'Rs. ' + Math.round(n).toLocaleString('en-PK');
const calcFuel = km => (km / FUEL_EFF) * FUEL_PKR;

// ── MAP INIT ──────────────────────────────────────────────────────
let mapCorp, mapDrv;
let ctrlR1Corp, ctrlR1Drv, ctrlR2Corp, ctrlR2Drv;

// Custom icons
function makeIcon(color) {
  return L.divIcon({
    html: `<div style="width:14px;height:14px;background:${color};border-radius:50%;border:2px solid #fff;box-shadow:0 0 8px ${color}88;"></div>`,
    iconAnchor:[7,7], className:''
  });
}

function initMaps() {
  // OSM standard tiles — road centerlines match LRM perfectly
  const OSM_TILE = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const OSM_ATTR = '&copy; <a href="https://openstreetmap.org/">OpenStreetMap</a> contributors';

  mapCorp = L.map('map-corp', {zoomControl:true}).setView([25.07,69.10],8);
  L.tileLayer(OSM_TILE,{attribution:OSM_ATTR,maxZoom:19}).addTo(mapCorp);

  mapDrv = L.map('map-drv', {zoomControl:false}).setView([25.07,69.10],8);
  L.tileLayer(OSM_TILE,{attribution:OSM_ATTR,maxZoom:19}).addTo(mapDrv);
  L.control.zoom({position:'bottomright'}).addTo(mapDrv);

  // Add start/end markers
  const greenIcon = makeIcon('#2D5016');
  const redIcon   = makeIcon('#C62828');
  [mapCorp, mapDrv].forEach(m => {
    L.marker(MITHI,{icon:greenIcon}).addTo(m).bindPopup('<b>Mithi</b><br>Departure Point');
    L.marker(HYD,  {icon:redIcon  }).addTo(m).bindPopup('<b>Hyderabad</b><br>Destination');
  });

  // Create Route 1 routing controls (Fastest — direct)
  ctrlR1Corp = createRouteControl(mapCorp, [MITHI, HYD], '#2D5016', 6, false);
  ctrlR1Drv  = createRouteControl(mapDrv,  [MITHI, HYD], '#4A7C2F', 6, false);

  // Create Route 2 routing controls (Via Naukot) — hidden initially
  ctrlR2Corp = createRouteControl(mapCorp, [MITHI, NAUKOT, HYD], '#1D4ED8', 5, true);
  ctrlR2Drv  = createRouteControl(mapDrv,  [MITHI, NAUKOT, HYD], '#3B82F6', 5, true);

  // Listen to route found events to get distance/duration
  ctrlR1Corp.on('routesfound', e => {
    const r = e.routes[0];
    state.routeInfo.r1 = {km:(r.summary.totalDistance/1000).toFixed(1), min:Math.round(r.summary.totalTime/60)};
    el('r1-meta').textContent = state.routeInfo.r1.km+' km · ~'+fmtMin(state.routeInfo.r1.min);
    el('corp-status').textContent = '✅ Road-aligned route loaded (OSRM)';
    el('drv-status').textContent  = '✅ Road-aligned route loaded (OSRM)';
    updateMetrics();
  });
  ctrlR1Corp.on('routingerror', () => {
    el('corp-status').textContent = '⚠️ Using fallback routing';
    el('drv-status').textContent  = '⚠️ Using fallback routing';
  });
  ctrlR2Corp.on('routesfound', e => {
    const r = e.routes[0];
    state.routeInfo.r2 = {km:(r.summary.totalDistance/1000).toFixed(1), min:Math.round(r.summary.totalTime/60)};
    el('r2-meta').textContent = state.routeInfo.r2.km+' km · ~'+fmtMin(state.routeInfo.r2.min);
  });

  setTimeout(() => { mapCorp.invalidateSize(); mapDrv.invalidateSize(); }, 200);
}

function fmtMin(m) {
  const h = Math.floor(m/60), min = m%60;
  return (h>0 ? h+'h ' : '') + min+'m';
}

function createRouteControl(map, waypoints, lineColor, weight, hidden) {
  const ctrl = L.Routing.control({
    waypoints: waypoints,
    router: L.Routing.osrmv1({
      serviceUrl: 'https://router.project-osrm.org/route/v1',
      profile: 'driving'
    }),
    lineOptions: {
      styles: [{ color: lineColor, weight: weight, opacity: hidden ? 0 : 0.9 }],
      extendToWaypoints: true,
      missingRouteTolerance: 0
    },
    createMarker: () => null,   // hide default A/B markers
    show: false,                // hide instructions panel
    addWaypoints: false,
    routeWhileDragging: false,
    fitSelectedRoutes: false,
    showAlternatives: false
  }).addTo(map);

  return ctrl;
}

// ── ROUTE SELECTION ───────────────────────────────────────────────
function selectRoute(n) {
  state.activeRoute = n;
  el('r1-opt').className = 'route-opt' + (n===1?' active':'');
  el('r2-opt').className = 'route-opt' + (n===2?' active':'');

  // Toggle line opacity
  const setOpacity = (ctrl, opacity) => {
    if (!ctrl) return;
    ctrl.getPlan && ctrl.getPlan(); // ensure plan exists
    const lines = ctrl._line;
    if (lines) lines.setStyle({opacity});
  };

  if (n === 1) {
    // Show R1 prominently, fade R2
    [ctrlR1Corp, ctrlR1Drv].forEach(c => c && c.setWaypoints && updateLineStyle(c,'#2D5016',6,0.9));
    [ctrlR2Corp, ctrlR2Drv].forEach(c => c && updateLineStyle(c,'#1D4ED8',3,0.2));
  } else {
    // Show R2 prominently, fade R1
    [ctrlR1Corp, ctrlR1Drv].forEach(c => c && updateLineStyle(c,'#2D5016',3,0.2));
    [ctrlR2Corp, ctrlR2Drv].forEach(c => c && updateLineStyle(c,'#1D4ED8',6,0.9));
  }
  updateMetrics();
}

function updateLineStyle(ctrl, color, weight, opacity) {
  try {
    // LRM stores the rendered line in _line property
    if (ctrl._line) ctrl._line.setStyle({color, weight, opacity});
    // Also update the options so re-renders use correct style
    ctrl.options.lineOptions.styles = [{color, weight, opacity}];
  } catch(e) { /* route not yet loaded */ }
}

// ── METRICS UPDATE ────────────────────────────────────────────────
function updateMetrics() {
  const ri  = state.routeInfo['r'+state.activeRoute];
  const tot = ri ? parseFloat(ri.km) : 162.5;
  const cov = parseFloat((tot * state.progressPct/100).toFixed(1));
  const rem = parseFloat((tot - cov).toFixed(1));

  let spd = 65;
  if (state.weather==='Rain' && state.time==='Night') spd = 42;
  else if (state.weather==='Rain' || state.time==='Night') spd = 55;

  const remMin = Math.round((rem/spd)*60);
  const etaStr = fmtMin(remMin);
  const fuel   = calcFuel(tot);
  let safety   = 88;
  if (state.weather==='Rain') safety -= 22;
  if (state.time==='Night')   safety -= 18;
  if (state.cargo==='Fragile') safety -= 5;
  safety = Math.max(20, safety);

  const safetyColor = safety<50?'#C62828':safety<70?'#E65100':'#2E7D32';
  const spdStr = spd+' km/h';

  // KPI Cards
  el('kpi-dist').textContent  = tot+' km';
  el('kpi-dist-d').textContent= '📍 Route '+state.activeRoute+' — '+cov+' km covered';
  el('kpi-eta').textContent   = etaStr;
  el('kpi-eta-d').textContent = spd<50?'▼ Slow — Adverse Conditions':'▼ On Schedule';
  el('kpi-fuel').textContent  = fmtPKR(fuel);
  el('kpi-safety').textContent  = safety+'%';
  el('kpi-safety').style.color  = safetyColor;
  el('kpi-safety-d').textContent= safety<50?'▼ Rain + Night Risk':'▲ Safe Conditions';
  el('kpi-safety-d').style.color= safetyColor;

  // Sidebar
  el('sb-fuel').textContent = fmtPKR(fuel);
  el('sb-dist').textContent = tot;

  // Progress
  const pct = state.progressPct;
  el('prog-fill').style.width  = pct+'%';
  el('prog-badge').textContent = pct+'% Completed';
  el('prog-covered').textContent = '📍 Covered: '+cov+' / '+tot+' km';
  el('prog-eta').textContent     = '⏱️ ETA: ~'+etaStr;

  // Telemetry
  el('tele-speed').textContent = spdStr+' (Limit: '+(spd<50?'50':'60')+')';
  el('tele-speed').style.color = spd<50?'#C62828':'#2E7D32';
  el('tele-road').textContent  = state.weather==='Rain'?'🌧️ Wet / Slippery (μ=0.38)':'✅ Dry (μ=0.72)';

  // Safety alert
  updateSafety();
}

// ── SAFETY ALERT ──────────────────────────────────────────────────
const SAFETY = {
  extreme: {cls:'extreme',icon:'⛔', sd:'INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal — Raftar 50% ghat karo. Hazard lights hinner chalao.', ur:'ANTEHAI KHATARNAK: Raat + Baarish + Nazuk Maal — Raftar 50% ghatayein.', dh:'BAHUT KHATRO: Raat + Barish — Raftar 50% ghat karo.', en:'EXTREME RISK: Night + Rain + Fragile Cargo — Reduce speed 50%. Hazard lights ON.'},
  critical:{cls:'critical',icon:'🛑', sd:'KHATARNAK: Highway te barish — Sadak chikani. Raftar 60 km/h.', ur:'KHATARNAK: Highway par baarish — Sadak phislan wali. Raftar 60 km/h.', dh:'KHATARNAK: Barish waro raah — Sadak chikani. Raftar 60 km/h.', en:'CRITICAL: Rain on Highway — Slippery road (μ=0.38). Speed limit 60 km/h.'},
  warning: {cls:'warning', icon:'⚠️', sd:'KHABARDAR: Raat driving — Raftar 60 km/h. Headlights tez chalao.', ur:'KHABARDAR: Raat gaari — Raftar 60 km/h. Headlights tez rakhein.', dh:'KHABARDAR: Raat driving — Raftar 60 km/h.', en:'WARNING: Night driving — Reduce speed to 60 km/h. High-beam ON.'},
  standard:{cls:'standard',icon:'ℹ️', sd:'MAMULI HALAT: Rasto saaf ahe. Speed limit manno. Salaamti halo!', ur:'MAMULI HALAT: Rasta saaf hai. Speed limit manein.', dh:'MAMULI HALAT: Raah saaf hai. Salaamti vanj!', en:'STANDARD: Road clear. Maintain speed limit. Drive safe!'}
};
function updateSafety() {
  let key='standard';
  if (state.weather==='Rain' && state.time==='Night') key='extreme';
  else if (state.weather==='Rain') key='critical';
  else if (state.time==='Night') key='warning';
  const t=SAFETY[key];
  const lk={Sindhi:'sd',Urdu:'ur',Dhatki:'dh',English:'en'}[state.lang]||'en';
  el('safety-panel').className='safety-alert '+t.cls;
  el('alert-icon').textContent  = t.icon;
  el('alert-title').textContent = t[lk];
  el('alert-body').textContent  = '';
}

// ── NLP ENGINE ────────────────────────────────────────────────────
function safeReply(obj) {
  try { return obj[state.lang]||obj.Urdu||obj.English||'📡 IDAS: Message received.'; }
  catch(e) { return '📡 IDAS: Network reconnecting… Please try again.'; }
}

function smartReply(txt) {
  const v   = (txt||'').toLowerCase();
  const ri  = state.routeInfo['r'+state.activeRoute];
  const tot = ri ? parseFloat(ri.km) : 162.5;
  const cov = parseFloat((tot*state.progressPct/100).toFixed(1));
  const rem = parseFloat((tot-cov).toFixed(1));
  let spd=65;
  if (state.weather==='Rain'&&state.time==='Night') spd=42;
  else if (state.weather==='Rain'||state.time==='Night') spd=55;
  const remMin=Math.round((rem/spd)*60), hrs=Math.floor(remMin/60), mins=remMin%60;
  const spdStr=spd+' km/h', fuelLeft=fmtPKR(calcFuel(rem));

  if (/route|rasto|raah|give|where|path|map|destination|way|kahan|location|mera/i.test(v))
    return {Sindhi:`🗺️ RASTO: Mithi→Hyderabad (${tot} km, Route ${state.activeRoute}). ${cov} km Digri wath puras. ${rem} km baaki. ETA: ${hrs}h ${mins}m.`,Urdu:`🗺️ RASTA: Mithi→Hyderabad (${tot} km, Route ${state.activeRoute}). ${cov} km Digri ke paas. ${rem} km baaqi. ETA: ${hrs}h ${mins}m.`,Dhatki:`🗺️ RAAH: Mithi→Hyderabad (${tot} km). ${cov} km pura. ${rem} km baaki.`,English:`🗺️ ROUTE [R${state.activeRoute}]: Mithi→Hyderabad (${tot} km). Covered: ${cov} km near Digri. Remaining: ${rem} km. ETA: ${hrs}h ${mins}m.`};
  if (/mura|side|direction|kayi|turn|left|right|khabbe|saje|modh/i.test(v))
    return {Sindhi:'🧭 DIRECTION: NH-8 te siddho vanj 45 km. Naukot junction te seedha — Matli taraf.',Urdu:'🧭 DIRECTION: Agle 45 km seedha NH-8. Naukot junction par seedhe rahein.',Dhatki:'🧭 DIRECTION: NH-8 te siddha vanj 45 km. Naukot te seedha raho.',English:'🧭 DIRECTION: Continue straight on NH-8 for 45 km. No turn at Naukot — head toward Matli.'};
  if (/speed|fast|slow|raftar|tez|limit|chalo/i.test(v))
    return {Sindhi:`⚡ RAFTAR: ${spdStr} (${state.weather}, ${state.time}). Achanak brake na kayo.`,Urdu:`⚡ RAFTAR: ${spdStr} (${state.weather}, ${state.time}). Mehfooz fasla rakhein.`,Dhatki:`⚡ RAFTAR: ${spdStr}. Tezi na karo.`,English:`⚡ SPEED: Recommended ${spdStr} — ${state.weather}, ${state.time}. Maintain 6-second gap.`};
  if (/time|eta|distance|km|pohchan|when|reach|ghante/i.test(v))
    return {Sindhi:`⏱️ ETA: ${hrs}h ${mins}m baaki. ${rem} km. Fuel: ${fuelLeft}.`,Urdu:`⏱️ ETA: ${hrs}h ${mins}m baaqi. ${rem} km. Fuel: ${fuelLeft}.`,Dhatki:`⏱️ ETA: ${hrs}h ${mins}m baaki. ${rem} km.`,English:`⏱️ ETA: ~${hrs}h ${mins}m to Hyderabad. Distance left: ${rem} km. Fuel remaining: ${fuelLeft}.`};
  if (/fuel|petrol|kharcha|paisa|rupay|pump/i.test(v))
    return {Sindhi:`⛽ PETROL: Baaki kharcha ${fuelLeft}. Aglo pump: Naukot (~18 km).`,Urdu:`⛽ PETROL: Baaki kharcha ${fuelLeft}. Agla pump: Naukot (~18 km).`,Dhatki:`⛽ PETROL: Baaki ${fuelLeft}. Aglo pump: Naukot.`,English:`⛽ FUEL: Remaining cost: ${fuelLeft}. Next station: Naukot (~18 km).`};
  if (/maal|tamatar|cargo|load|tomato|fragile/i.test(v))
    return {Sindhi:`🍅 MAAL: ${state.cargo}. Temp: 19.2°C ✅. Achanak brake na kayo.`,Urdu:`🍅 MAAL: ${state.cargo}. Temp: 19.2°C ✅. Achanak brake mat.`,Dhatki:`🍅 MAAL: ${state.cargo}. Temp: 19.2°C. Brake ahista karo.`,English:`🍅 CARGO: ${state.cargo} loaded. Temp: 19.2°C ✅. Avoid harsh braking.`};
  if (/weather|rain|barish|mosam|night|raat|dark/i.test(v))
    return {Sindhi:`🌧️ MOSAM: ${state.weather} (${state.time}). Sadak chikani (μ=0.38). Hazard lights on.`,Urdu:`🌧️ MAUSAM: ${state.weather} (${state.time}). Sadak phislan wali. Hazard lights on.`,Dhatki:`🌧️ MOSAM: ${state.weather}. Sadak chikani. Hazard lights on.`,English:`🌧️ WEATHER: ${state.weather}, ${state.time}. Road friction μ=0.38. Stopping distance 2×. Hazard lights ON.`};
  if (/hello|hi|salam|aayo|kiin|welcome|khush/i.test(v))
    return {Sindhi:`👋 IDAS: Khush aayo TRK-119! Route ${state.activeRoute} active — ${state.progressPct}% mukammal. Kihn madad kayo?`,Urdu:`👋 IDAS: Khush aamdeed TRK-119! Route ${state.activeRoute} — ${state.progressPct}% mukammal. Kaise madad karein?`,Dhatki:`👋 IDAS: Aavkaari TRK-119! Route ${state.activeRoute}. Kihn madad karo?`,English:`👋 IDAS: Welcome TRK-119! Route ${state.activeRoute} active — ${state.progressPct}% complete. How can dispatch assist?`};
  if (/kharab|breakdown|help|madad|emergency|accident|jam|hazard|khatro/i.test(v))
    return {Sindhi:`🚨 HIGH ALERT: TRK-119 ${cov} km wath khatro. Diplo rasto. Naukot Police (~12 km). Saabit raho.`,Urdu:`🚨 HIGH ALERT: TRK-119 ${cov} km par hazard. Diplo se alternate. Naukot Police (~12 km).`,Dhatki:`🚨 HIGH ALERT: TRK-119 ${cov} km paas khatro. Diplo raah. Saabit raho.`,English:`🚨 HIGH ALERT: Hazard at ${cov} km (TRK-119). Alternate via Diplo computed. Naukot Police ~12 km. Stay calm.`};
  return {Sindhi:`📡 DISPATCH: TRK-119 paighaam record. Route ${state.activeRoute} — ${cov} km (${state.progressPct}%). Raftar: ${spdStr}. ETA: ${hrs}h ${mins}m.`,Urdu:`📡 DISPATCH: TRK-119 record. Route ${state.activeRoute} — ${cov} km (${state.progressPct}%). Raftar: ${spdStr}. ETA: ${hrs}h ${mins}m.`,Dhatki:`📡 DISPATCH: TRK-119 sandesh record. ${cov} km (${state.progressPct}%). Raftar: ${spdStr}.`,English:`📡 DISPATCH: Message logged TRK-119. Route ${state.activeRoute} — ${cov} km of ${tot} km (${state.progressPct}%). Speed: ${spdStr}. ETA: ${hrs}h ${mins}m. Fuel: ${fuelLeft}.`};
}

// ── CHAT ──────────────────────────────────────────────────────────
function renderChat() {
  ['corp','drv'].forEach(w => {
    const box=el(w+'-chat-box');
    let h='';
    state.messages.forEach(m => {
      const isDrv=m.role==='driver';
      const txt = w==='corp'
        ? (isDrv?m.original:m.english)
        : (isDrv?m.original:safeReply(m.replyObj||{English:m.english,Sindhi:m.english,Urdu:m.english,Dhatki:m.english}));
      h+=`<div class="chat-row ${isDrv?'driver':'corporate'}">
        <div class="chat-avatar">${isDrv?'🚚':'🏢'}</div>
        <div>
          <div class="chat-bubble">${txt}</div>
          <div class="chat-meta">${isDrv?(w==='corp'?'🌐 '+state.lang+' → EN':'You ('+state.lang+')'):(w==='corp'?'🏢 Dispatch EN':'🏢 → '+state.lang)}</div>
        </div></div>`;
    });
    box.innerHTML=h||'<div style="text-align:center;color:#9CA3AF;padding:20px;font-size:0.78rem;">No messages yet.</div>';
    box.scrollTop=box.scrollHeight;
  });
}

function sendDrvMessage(e) {
  e.preventDefault();
  const inp=el('drv-chat-input'), v=inp.value.trim(); if(!v) return;
  const ro=smartReply(v), isH=/kharab|breakdown|help|madad|emergency|accident|hazard|khatro/i.test(v);
  state.messages.push({role:'driver',original:(isH?'🚨 ':'')+v,english:(isH?'🚨 HAZARD: ':'')+v});
  state.messages.push({role:'corporate',english:ro.English,replyObj:ro});
  inp.value=''; renderChat();
}

function sendCorpMessage(e) {
  e.preventDefault();
  const inp=el('corp-chat-input'), v=inp.value.trim(); if(!v) return;
  const ro={English:'✅ Advisory received by TRK-119.',Sindhi:'✅ Advisory TRK-119 khe mili.',Urdu:'✅ Advisory TRK-119 ko mili.',Dhatki:'✅ Advisory TRK-119 khe mili.'};
  state.messages.push({role:'corporate',english:'🏢 DISPATCH: '+v,replyObj:{English:'🏢 DISPATCH: '+v,Sindhi:'🏢 DISPATCH: '+v,Urdu:'🏢 DISPATCH: '+v,Dhatki:'🏢 DISPATCH: '+v}});
  state.messages.push({role:'driver',original:safeReply(ro),english:ro.English});
  inp.value=''; renderChat();
}

// ── CONTROLS ──────────────────────────────────────────────────────
function onCtrlChange() {
  state.lang    = el('sel-lang').value;
  state.cargo   = el('sel-cargo').value;
  state.time    = el('sel-time').value;
  state.weather = el('sel-weather').value;
  el('drv-chat-title').textContent = '💬 Dispatch Chat ('+state.lang+')';
  updateMetrics(); renderChat();
}
function updateProgress(v) { state.progressPct=parseInt(v); updateMetrics(); }
function switchTab(tab) {
  el('tab-corp').style.display = tab==='corp'?'block':'none';
  el('tab-drv').style.display  = tab==='drv'?'block':'none';
  el('tab-corp-btn').className = 'tab-btn'+(tab==='corp'?' active':'');
  el('tab-drv-btn').className  = 'tab-btn'+(tab==='drv'?' active':'');
  setTimeout(()=>{mapCorp&&mapCorp.invalidateSize();mapDrv&&mapDrv.invalidateSize();},150);
}

// ── AUDIO ─────────────────────────────────────────────────────────
function playAudio() {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const lm={Sindhi:'ur-PK',Urdu:'ur-PK',Dhatki:'ur-PK',English:'en-US'};
  const msgs={Sindhi:'IDAS Alert TRK-119 laye. NH-8 te barish. Raftar ghat karo. Salaamti saan halo.',Urdu:'IDAS Alert Truck 119. NH-8 par baarish. Raftar ghatayein. Salamti se chalein.',Dhatki:'IDAS Alert TRK-119. NH-8 te barish. Raftar ghat karo.',English:'IDAS Alert for Truck 119. Rain on National Highway 8. Reduce speed. Drive safely.'};
  const utt=new SpeechSynthesisUtterance(msgs[state.lang]);
  utt.lang=lm[state.lang]; utt.rate=0.88;
  window.speechSynthesis.speak(utt);
  el('audio-text').textContent='🔊 Playing: '+msgs[state.lang];
}

// ── BOOT ──────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initMaps();
  updateMetrics();
  renderChat();
});
window.addEventListener('resize', () => {
  setTimeout(()=>{mapCorp&&mapCorp.invalidateSize();mapDrv&&mapDrv.invalidateSize();},200);
});
</script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

size = len(HTML)
lines = HTML.count('\n')
print(f'SUCCESS — index.html: {size:,} bytes, {lines} lines')
print('Key features:')
print('  [OK] Leaflet Routing Machine — auto road-snapped routing via OSRM')
print('  [OK] Route 1 (Fastest: green) + Route 2 (Via Naukot: blue)')
print('  [OK] LRM control panel hidden — only route line shown')
print('  [OK] Original UI: sidebar, tab-bar, KPI cards, safety alert, telemetry')
print('  [OK] Fuel cost calculator (Rs.282/L, 8km/L)')
print('  [OK] 10-intent trilingual NLP with language fallback chain')
print('  [OK] OSM tiles (same tile layer as LRM — roads match perfectly)')
