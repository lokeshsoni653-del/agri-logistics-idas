"""
Agri-Logistics IDAS — Intelligent Driver Assistance System
Streamlit UI Layout & State Management (Phase 3 - Context-Aware Safety)
"""

import streamlit as st
from routing import get_osrm_route, plot_route_on_map
from voice_advisory import generate_voice_advisory

# ─────────────────────────────────────────────
# MOCK TRANSLATOR LOGIC
# ─────────────────────────────────────────────
def mock_translate(text: str, target_lang: str) -> str:
    """Simulates a bidirectional NLP translation layer for logistics."""
    t = text.lower().strip()
    
    # Driver reports hazard -> Translates to English for Corporate
    if t in ["pul budi wai ahe", "pul doob gaya hai", "pul budi gayo hai"]:
        return "⚠️ The bridge is flooded."
        
    # Corporate sends update -> Translates to Native for Driver
    if t in ["delay tomato pickup by 2 hours", "delay pickup"]:
        translations = {
            "Sindhi": "Tamatar kahn me 2 kalak di dair ahe",
            "Urdu": "Tamatar uthane mein 2 ghante ki der hai",
            "Dhatki": "Tamatar uparan mein 2 kalak ro vilamb hai"
        }
        return translations.get(target_lang, text)
        
    # Generic Fallback
    if target_lang == "English":
        return f"[Translated to English]: {text}"
    else:
        return f"[Translated to {target_lang}]: {text}"

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Agri-Logistics IDAS",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App background ── */
    .stApp {
        background-color: #F5F2EC;
    }

    /* ── Top banner ── */
    .app-header {
        background: linear-gradient(135deg, #2D5016 0%, #4A7C2F 60%, #6B9E3F 100%);
        border-radius: 12px;
        padding: 20px 32px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .app-header h1 {
        color: #FFFFFF;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .app-header p {
        color: #C5DFA0;
        font-size: 0.85rem;
        margin: 4px 0 0 0;
    }
    .header-badge {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }

    /* ── Tabs styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #EAE6DE;
        border-radius: 10px;
        padding: 6px;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #5C6B4A;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 10px 24px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #2D5016 !important;
        box-shadow: 0 2px 8px rgba(45, 80, 22, 0.12);
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid #4A7C2F;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-card h3 {
        color: #8A9E78;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 0 0 6px 0;
    }
    .metric-card .metric-value {
        color: #1E3A0F;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        margin: 0 0 4px 0;
    }
    .metric-card .metric-delta {
        color: #4A7C2F;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* ── Section cards ── */
    .section-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 16px;
    }
    .section-card h4 {
        color: #2D5016;
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0 0 12px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid #EAE6DE;
    }
    .section-card p, .section-card li {
        color: #6B7A5C;
        font-size: 0.875rem;
        line-height: 1.6;
        margin: 4px 0;
    }

    /* ── Status pills ── */
    .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .pill-green  { background: #D6EFC4; color: #2D6A1A; }
    .pill-orange { background: #FDE8C8; color: #8A4800; }
    .pill-red    { background: #FDD5D5; color: #8A0000; }
    .pill-blue   { background: #D0E8FF; color: #004A8A; }

    /* ── Driver panel ── */
    .driver-panel {
        background: linear-gradient(160deg, #1E3A0F 0%, #2D5016 100%);
        border-radius: 16px;
        padding: 28px;
        color: #FFFFFF;
        margin-bottom: 20px;
    }
    .driver-panel h2 {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0 0 4px 0;
    }
    .driver-panel .sub {
        color: #A8C87E;
        font-size: 0.82rem;
        margin: 0;
    }
    .driver-info-row {
        display: flex;
        gap: 24px;
        margin-top: 18px;
        flex-wrap: wrap;
    }
    .driver-info-item label {
        color: #8AB065;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        display: block;
        margin-bottom: 3px;
    }
    .driver-info-item span {
        color: #FFFFFF;
        font-size: 0.92rem;
        font-weight: 600;
    }

    /* ── Cargo type badges ── */
    .cargo-standard {
        background: #D6EFC4; 
        color: #2D6A1A;
        padding: 6px 14px; 
        border-radius: 8px;
        font-weight: 600; 
        font-size: 0.85rem; 
        display: inline-block;
    }
    .cargo-fragile {
        background: #FDE8C8; 
        color: #8A4800;
        padding: 6px 14px; 
        border-radius: 8px;
        font-weight: 600; 
        font-size: 0.85rem; 
        display: inline-block;
    }

    /* ── Placeholder text blocks ── */
    .placeholder-block {
        background: #F0EDE6;
        border: 2px dashed #C8C0A8;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: #9A9280;
        font-size: 0.82rem;
        font-style: italic;
        margin-top: 8px;
    }

    /* ── Divider ── */
    hr.agri-hr {
        border: none;
        border-top: 1px solid #DDD8CD;
        margin: 16px 0;
    }

    /* ── Streamlit selectbox / label overrides ── */
    label[data-testid="stWidgetLabel"] > div > p {
        font-weight: 600 !important;
        color: #2D5016 !important;
        font-size: 0.875rem !important;
    }

    /* ── Dynamic Safety Alert Panel ── */
    .safety-alert {
        border-radius: 10px; 
        padding: 18px 20px; 
        margin-bottom: 16px; 
        display: flex; 
        align-items: flex-start; 
        gap: 14px; 
        border-left: 5px solid;
    }
    .safety-alert.standard { 
        background: #E8F4FD; 
        border-color: #2196F3; 
        color: #0C4375; 
    }
    .safety-alert.warning { 
        background: #FFF4E5; 
        border-color: #FF9800; 
        color: #804C00; 
    }
    .safety-alert.critical { 
        background: #FDECEA; 
        border-color: #F44336; 
        color: #7A1911; 
    }
    .safety-icon { 
        font-size: 1.8rem; 
        line-height: 1; 
    }
    .safety-text h5 { 
        margin: 0 0 6px 0; 
        font-size: 0.95rem; 
        font-weight: 700; 
    }
    .safety-text p { 
        margin: 0; 
        font-size: 0.85rem; 
        line-height: 1.5; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS = {
    "driver_language": "Sindhi",
    "cargo_type": "Standard",
    "time_of_day": "Day",
    "weather": "Clear",
    "driver_name": "Muhammad Saleem",
    "driver_id": "DRV-0042",
    "vehicle_id": "TRK-119",
    "current_route": "Hyderabad → Karachi",
    "chat_messages": [
        {
            "role": "corporate", 
            "original": "Welcome to IDAS Network.", 
            "english": "Welcome to IDAS Network.", 
            "source_lang": "English"
        }
    ]
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

LANGUAGES = ["Sindhi", "Urdu", "Dhatki"]
CARGO_TYPES = ["Standard", "Fragile / Tomatoes"]
TIME_OPTS = ["Day", "Night"]
WEATHER_OPTS = ["Clear", "Rain"]
CARGO_LABELS = {
    "Standard":            ("cargo-standard", "📦 Standard"),
    "Fragile / Tomatoes":  ("cargo-fragile",  "🍅 Fragile / Tomatoes"),
}
LANG_FLAG = {"Sindhi": "🟢", "Urdu": "🔵", "Dhatki": "🟡"}

st.markdown(
    """
    <div class="app-header">
        <div>
            <h1>🌾 Agri-Logistics IDAS</h1>
            <p>Intelligent Driver Assistance System — Sindh Agricultural Supply Chain</p>
        </div>
        <div class="header-badge">PHASE 3 · FULL SYSTEM</div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_corp, tab_driver = st.tabs(["🏢 Corporate Dashboard", "🚚 Driver Interface"])

# ═══════════════════════════════════════════════
# TAB 1 — CORPORATE DASHBOARD
# ═══════════════════════════════════════════════
with tab_corp:
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("ACTIVE TRUCKS",    "24",   "↑ 3 since yesterday",  "#4A7C2F"),
        ("DELIVERIES",       "138",  "↑ 12% vs last week",   "#4A7C2F"),
        ("IN TRANSIT",       "17",   "On scheduled routes",  "#6B5E2F"),
        ("HAZARDS",          "1",    "⚠ Requires attention", "#8A3A1A"),
    ]
    
    for col, (label, value, delta, accent) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color:{accent};">
                    <h3>{label}</h3>
                    <p class="metric-value">{value}</p>
                    <p class="metric-delta">{delta}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

    st.markdown("<hr class='agri-hr' style='margin:22px 0;'>", unsafe_allow_html=True)

    col_map, col_fleet = st.columns([1.6, 1], gap="large")

    with col_map:
        st.markdown("<div class='section-card'><h4>🗺️ Live Fleet Map</h4>", unsafe_allow_html=True)
        
        with st.spinner("Calculating true-road network distance..."):
            route_data = get_osrm_route() 
            if route_data["success"]:
                plot_route_on_map(route_geometry=route_data["geometry"])
                st.session_state["route_instructions"] = route_data["instructions"]
            else:
                st.error(route_data["error"])
                
        st.markdown("</div>", unsafe_allow_html=True)

    with col_fleet:
        st.markdown(
            """
            <div class="section-card">
                <h4>🚛 Fleet Status</h4>
                <p>TRK-101 &nbsp;<span class="pill pill-green">On Route</span></p>
                <p>TRK-115 &nbsp;<span class="pill pill-orange">Delayed</span></p>
                <p>TRK-119 &nbsp;<span class="pill pill-green">On Route</span></p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # ── CORPORATE CHAT INTERFACE ──
        st.markdown("<div class='section-card'><h4>💬 Dispatch Chat (English View)</h4>", unsafe_allow_html=True)
        
        chat_container_corp = st.container(height=300)
        for msg in st.session_state.chat_messages:
            with chat_container_corp.chat_message("assistant" if msg["role"] == "corporate" else "user"):
                st.write(msg["english"])
                if msg["role"] == "driver":
                    st.caption(f"*(Translated from {msg['source_lang']})*")
        
        if prompt := st.chat_input("Message TRK-119 driver (English)...", key="corp_input"):
            st.session_state.chat_messages.append({
                "role": "corporate", 
                "original": prompt, 
                "english": prompt, 
                "source_lang": "English"
            })
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 2 — DRIVER INTERFACE
# ═══════════════════════════════════════════════
with tab_driver:
    lang_flag  = LANG_FLAG.get(st.session_state["driver_language"], "🟢")
    cargo_cls, cargo_lbl = CARGO_LABELS.get(st.session_state["cargo_type"], CARGO_LABELS["Standard"])

    st.markdown(
        f"""
        <div class="driver-panel">
            <h2>👤 {st.session_state['driver_name']}</h2>
            <div class="driver-info-row">
                <div class="driver-info-item">
                    <label>Current Route</label>
                    <span>{st.session_state['current_route']}</span>
                </div>
                <div class="driver-info-item">
                    <label>Language</label>
                    <span>{lang_flag} {st.session_state['driver_language']}</span>
                </div>
                <div class="driver-info-item">
                    <label>Cargo</label>
                    <span class="{cargo_cls}">{cargo_lbl}</span>
                </div>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # ── Settings row (Expanded with Context Simulators) ──
    col_lang, col_cargo, col_time, col_weather = st.columns(4, gap="medium")

    with col_lang:
        selected_lang = st.selectbox(
            "🌐 Language", 
            options=LANGUAGES, 
            index=LANGUAGES.index(st.session_state["driver_language"]), 
            key="_lang_select"
        )
        if selected_lang != st.session_state["driver_language"]:
            st.session_state["driver_language"] = selected_lang
            st.rerun()

    with col_cargo:
        selected_cargo = st.selectbox(
            "📦 Cargo", 
            options=CARGO_TYPES, 
            index=CARGO_TYPES.index(st.session_state["cargo_type"]), 
            key="_cargo_select"
        )
        if selected_cargo != st.session_state["cargo_type"]:
            st.session_state["cargo_type"] = selected_cargo
            st.rerun()
            
    with col_time:
        selected_time = st.selectbox(
            "⏱️ Time (Simulate)", 
            options=TIME_OPTS, 
            index=TIME_OPTS.index(st.session_state["time_of_day"]), 
            key="_time_select"
        )
        if selected_time != st.session_state["time_of_day"]:
            st.session_state["time_of_day"] = selected_time
            st.rerun()

    with col_weather:
        selected_weather = st.selectbox(
            "☁️ Weather (Sim)", 
            options=WEATHER_OPTS, 
            index=WEATHER_OPTS.index(st.session_state["weather"]), 
            key="_weather_select"
        )
        if selected_weather != st.session_state["weather"]:
            st.session_state["weather"] = selected_weather
            st.rerun()

    st.markdown("<hr class='agri-hr'>", unsafe_allow_html=True)

    # ── DYNAMIC CONTEXT-AWARE SAFETY ETIQUETTE ──
    # Evaluate context and determine alert level
    alert_level = "standard"
    alert_icon = "ℹ️"
    alert_title = "Standard Driving Parameters"
    alert_msg = "Route is clear. Maintain standard driving etiquette and observe local speed limits."

    if st.session_state["cargo_type"] == "Fragile / Tomatoes" and st.session_state["weather"] == "Rain":
        alert_level = "critical"
        alert_icon = "🛑"
        alert_title = "CRITICAL: Wet Roads + Fragile Cargo"
        alert_msg = "Roads are slippery and cargo is highly perishable. Reduce speed by 30%, increase following distance to 6 seconds, and avoid sudden braking."
    elif st.session_state["cargo_type"] == "Fragile / Tomatoes":
        alert_level = "warning"
        alert_icon = "🍅"
        alert_title = "CAUTION: Delicate Payload"
        alert_msg = "Perishable produce detected. Brake gently approaching turns and avoid sudden acceleration to prevent crop bruising."
    elif st.session_state["time_of_day"] == "Night" and st.session_state["weather"] == "Rain":
        alert_level = "critical"
        alert_icon = "🌧️"
        alert_title = "SEVERE: Low Visibility"
        alert_msg = "Nighttime and heavy rain detected. Turn on fog lights, avoid overtaking on single-lane roads, and watch for unlit agricultural vehicles."
    elif st.session_state["time_of_day"] == "Night":
        alert_level = "warning"
        alert_icon = "🌙"
        alert_title = "NIGHT ETIQUETTE ACTIVE"
        alert_msg = "Sun has set. Activate headlights, beware of stray livestock on rural roads, and dim high-beams for oncoming traffic."
    elif st.session_state["weather"] == "Rain":
        alert_level = "warning"
        alert_icon = "🌦️"
        alert_title = "WET CONDITIONS"
        alert_msg = "Light rain detected along route. Braking distance is increased. Please drive carefully."

    # Render the dynamic alert
    st.markdown(
        f"""
        <div class="safety-alert {alert_level}">
            <div class="safety-icon">{alert_icon}</div>
            <div class="safety-text">
                <h5>{alert_title}</h5>
                <p>{alert_msg}</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # ── Main driver columns ──
    col_nav, col_assist = st.columns([1.4, 1], gap="large")

    with col_nav:
        st.markdown(
            """
            <div class="section-card">
                <h4>🗺️ Navigation View</h4>
                <div class="placeholder-block" style="height:240px; display:flex; align-items:center; justify-content:center; flex-direction:column; gap:8px;">
                    <span style="font-size:2rem;">🧭</span>
                    <span>Turn-by-turn map will render here</span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col_assist:
        st.markdown(
            f"<div class='section-card'><h4>💬 Dispatch Chat ({st.session_state['driver_language']})</h4>", 
            unsafe_allow_html=True
        )
        
        target_lang = st.session_state["driver_language"]
        chat_container_drv = st.container(height=180)
        
        for msg in st.session_state.chat_messages:
            is_user = (msg["role"] == "driver")
            with chat_container_drv.chat_message("user" if is_user else "assistant"):
                if msg["source_lang"] == "English":
                    st.write(mock_translate(msg["english"], target_lang))
                else:
                    st.write(msg["original"])

        if prompt := st.chat_input(f"Type hazard in {target_lang}...", key="driver_input"):
            english_translation = mock_translate(prompt, "English")
            st.session_state.chat_messages.append({
                "role": "driver", 
                "original": prompt, 
                "english": english_translation, 
                "source_lang": target_lang
            })
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

    col_audio, col_tele = st.columns(2, gap="large")

    with col_audio:
        st.markdown("<div class='section-card'><h4>🔊 Audio Guidance</h4>", unsafe_allow_html=True)
        instructions = st.session_state.get("route_instructions", [])

        if instructions and len(instructions) > 1:
            st.write(f"**Next Turn:** {instructions[1]}")
            
            if st.button("🔊 Play Translated Instruction", type="primary"):
                result = generate_voice_advisory(
                    base_instruction=instructions[1], 
                    language=st.session_state["driver_language"],
                    cargo_type=st.session_state["cargo_type"]
                )
                
                if result["success"]:
                    st.success(f"**Translated ({result['language']}):** {result['text']}")
                    st.audio(result["audio_buffer"], format="audio/mp3") 
                else:
                    st.error(result["error"])
        else:
            st.info("⚠️ Map must be loaded in Corporate Dashboard to fetch route.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tele:
        st.markdown(
            """
            <div class="section-card">
                <h4>📡 Vehicle Telemetry</h4>
                <p><strong>Speed:</strong> — km/h</p>
                <p><strong>Engine temp:</strong> — °C</p>
                <div class="placeholder-block" style="height:20px; display:flex; align-items:center; justify-content:center;">
                    Live OBD feed — Phase 2
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    """
    <hr style="border:none; border-top:1px solid #DDD8CD; margin-top:32px;">
    <p style="text-align:center; color:#B0A890; font-size:0.75rem; padding-bottom:12px;">
        Agri-Logistics IDAS &nbsp;·&nbsp; Phase 3 Prototype &nbsp;·&nbsp; Sindh Agricultural Supply Chain
    </p>
    """,
    unsafe_allow_html=True,
)
