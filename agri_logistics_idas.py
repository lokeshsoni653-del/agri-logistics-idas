"""
Agri-Logistics IDAS — Intelligent Driver Assistance System
Streamlit UI Layout & State Management (Phase 1)
"""

import streamlit as st
from routing import get_osrm_route, plot_route_on_map
from voice_advisory import generate_voice_advisory

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
# CUSTOM CSS — earthy agri palette + utility
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
        background: #D6EFC4; color: #2D6A1A;
        padding: 6px 14px; border-radius: 8px;
        font-weight: 600; font-size: 0.85rem; display: inline-block;
    }
    .cargo-fragile {
        background: #FDE8C8; color: #8A4800;
        padding: 6px 14px; border-radius: 8px;
        font-weight: 600; font-size: 0.85rem; display: inline-block;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# SESSION STATE — initialise all keys once
# ─────────────────────────────────────────────
DEFAULTS = {
    # Driver settings
    "driver_language": "Sindhi",
    "cargo_type": "Standard",
    # Driver identity (placeholder until real auth)
    "driver_name": "Muhammad Saleem",
    "driver_id": "DRV-0042",
    "vehicle_id": "TRK-119",
    "current_route": "Hyderabad → Karachi",
    # Corporate filters (placeholder)
    "corp_date_filter": "Today",
    "corp_fleet_filter": "All Vehicles",
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
LANGUAGES = ["Sindhi", "Urdu", "Dhatki"]

CARGO_TYPES = ["Standard", "Fragile / Tomatoes"]

CARGO_LABELS = {
    "Standard":            ("cargo-standard", "📦 Standard"),
    "Fragile / Tomatoes":  ("cargo-fragile",  "🍅 Fragile / Tomatoes"),
}

# Language display names (for UI acknowledgment)
LANG_FLAG = {"Sindhi": "🟢", "Urdu": "🔵", "Dhatki": "🟡"}

# ─────────────────────────────────────────────
# HEADER BANNER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <div>
            <h1>🌾 Agri-Logistics IDAS</h1>
            <p>Intelligent Driver Assistance System — Sindh Agricultural Supply Chain</p>
        </div>
        <div class="header-badge">PHASE 1 · UI PROTOTYPE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────
tab_corp, tab_driver = st.tabs(["🏢 Corporate Dashboard", "🚚 Driver Interface"])


# ═══════════════════════════════════════════════
# TAB 1 — CORPORATE DASHBOARD
# ═══════════════════════════════════════════════
with tab_corp:

    # ── Sub-header ──
    st.markdown(
        "<p style='color:#5C6B4A; font-size:0.85rem; margin-bottom:18px;'>"
        "Real-time fleet overview, delivery performance, and cargo monitoring across all active routes.</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Row ──
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("ACTIVE TRUCKS",    "24",   "↑ 3 since yesterday",  "#4A7C2F"),
        ("DELIVERIES TODAY", "138",  "↑ 12% vs last week",   "#4A7C2F"),
        ("IN TRANSIT",       "17",   "On scheduled routes",  "#6B5E2F"),
        ("ALERTS",           "3",    "⚠ Requires attention", "#8A3A1A"),
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
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='agri-hr' style='margin:22px 0;'>", unsafe_allow_html=True)

    # ── Map + Fleet columns ──
    col_map, col_fleet = st.columns([1.6, 1], gap="large")

    with col_map:
        st.markdown("<div class='section-card'><h4>🗺️ Live Fleet Map</h4>", unsafe_allow_html=True)
        
        # Call the routing API for the Mithi -> Hyderabad corridor
        with st.spinner("Calculating true-road network distance..."):
            route_data = get_osrm_route() 
            
            if route_data["success"]:
                # Draw the actual map
                plot_route_on_map(route_geometry=route_data["geometry"])
                # Save the text instructions to Streamlit's memory for the Driver Tab to use
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
                <p>TRK-204 &nbsp;<span class="pill pill-red">Alert</span></p>
                <p>TRK-312 &nbsp;<span class="pill pill-blue">Loading</span></p>
                <p>TRK-408 &nbsp;<span class="pill pill-green">On Route</span></p>
                <div class="placeholder-block" style="margin-top:12px;">
                    Full fleet list — Phase 2
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Route analytics + Cargo breakdown ──
    col_routes, col_cargo = st.columns(2, gap="large")

    with col_routes:
        st.markdown(
            """
            <div class="section-card">
                <h4>📊 Route Analytics</h4>
                <div class="placeholder-block" style="height:140px; display:flex; align-items:center; justify-content:center; flex-direction:column; gap:6px;">
                    <span style="font-size:1.6rem;">📈</span>
                    <span>Delivery timeline chart — Phase 2</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_cargo:
        st.markdown(
            """
            <div class="section-card">
                <h4>🍅 Cargo Breakdown</h4>
                <p><strong>Standard loads:</strong> 89 active shipments</p>
                <p><strong>Fragile / Tomatoes:</strong> 49 active shipments</p>
                <div class="placeholder-block" style="height:80px; display:flex; align-items:center; justify-content:center; gap:6px; margin-top:10px;">
                    <span>Donut chart — Phase 2</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Alerts panel ──
    st.markdown(
        """
        <div class="section-card">
            <h4>⚠️ Active Alerts</h4>
            <p>🔴 &nbsp;<strong>TRK-204</strong> — Sudden braking event detected on M-9 near Gharo. Driver notified.</p>
            <p>🟠 &nbsp;<strong>TRK-115</strong> — 38-minute delay due to toll congestion at Karachi East.</p>
            <p>🟡 &nbsp;<strong>TRK-309</strong> — Cargo temperature deviation flagged (refrigerated load). Investigating.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════
# TAB 2 — DRIVER INTERFACE
# ═══════════════════════════════════════════════
with tab_driver:

    # ── Driver identity panel ──
    lang_flag  = LANG_FLAG.get(st.session_state["driver_language"], "🟢")
    cargo_cls, cargo_lbl = CARGO_LABELS.get(
        st.session_state["cargo_type"],
        CARGO_LABELS["Standard"],
    )

    st.markdown(
        f"""
        <div class="driver-panel">
            <h2>👤 {st.session_state['driver_name']}</h2>
            <p class="sub">Driver session active — selections below update live</p>
            <div class="driver-info-row">
                <div class="driver-info-item">
                    <label>Driver ID</label>
                    <span>{st.session_state['driver_id']}</span>
                </div>
                <div class="driver-info-item">
                    <label>Vehicle</label>
                    <span>{st.session_state['vehicle_id']}</span>
                </div>
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
        unsafe_allow_html=True,
    )

    # ── Settings row ──
    col_lang, col_cargo, col_gap = st.columns([1, 1, 1.5], gap="large")

    with col_lang:
        selected_lang = st.selectbox(
            "🌐 Select Language",
            options=LANGUAGES,
            index=LANGUAGES.index(st.session_state["driver_language"]),
            help="The driver interface audio and on-screen text will use this language.",
            key="_lang_select",
        )
        if selected_lang != st.session_state["driver_language"]:
            st.session_state["driver_language"] = selected_lang
            st.rerun()

    with col_cargo:
        selected_cargo = st.selectbox(
            "📦 Cargo Type",
            options=CARGO_TYPES,
            index=CARGO_TYPES.index(st.session_state["cargo_type"]),
            help="Fragile / Tomatoes mode enables gentler driving alerts and extra handling reminders.",
            key="_cargo_select",
        )
        if selected_cargo != st.session_state["cargo_type"]:
            st.session_state["cargo_type"] = selected_cargo
            st.rerun()

    # Contextual hint under cargo selector
    if st.session_state["cargo_type"] == "Fragile / Tomatoes":
        st.info(
            "🍅 **Fragile mode active.** "
            "Speed and braking thresholds are adjusted for delicate produce. "
            "Audio reminders will be issued in **{}**.".format(st.session_state["driver_language"]),
            icon=None,
        )
    else:
        st.success(
            "📦 **Standard cargo mode.** "
            "Normal driving parameters apply. "
            "Audio guidance language: **{}**.".format(st.session_state["driver_language"]),
            icon=None,
        )

    st.markdown("<hr class='agri-hr'>", unsafe_allow_html=True)

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
                    <span style="font-size:0.72rem;">(Phase 2 — Route overlay integration)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_assist:
        st.markdown(
            """
            <div class="section-card">
                <h4>🔔 Driver Alerts</h4>
                <p>✅ &nbsp;Route is clear ahead</p>
                <p>⚠️ &nbsp;Speed bump in 200 m</p>
                <p>🌧️ &nbsp;Light rain expected near Thatta</p>
                <p>⛽ &nbsp;Fuel station in 4 km (right side)</p>
                <div class="placeholder-block" style="margin-top:10px;">
                    Live alerts feed — Phase 2
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Audio & Telemetry placeholders ──
    col_audio, col_tele = st.columns(2, gap="large")

    with col_audio:
        st.markdown("<div class='section-card'><h4>🔊 Audio Guidance</h4>", unsafe_allow_html=True)
        
        # Grab the route instructions we saved in the Corporate tab
        instructions = st.session_state.get("route_instructions", [])

        if instructions:
            if len(instructions) > 1:
                st.write(f"**Next Turn:** {instructions[1]}") # Show the next step in English
                
                if st.button("🔊 Play Translated Instruction", type="primary"):
                    # Pass the English text, chosen language, and cargo type to the AI Voice Engine
                    result = generate_voice_advisory(
                        base_instruction=instructions[1], 
                        language=st.session_state["driver_language"],
                        cargo_type=st.session_state["cargo_type"]
                    )
                    
                    if result["success"]:
                        st.success(f"**Translated ({result['language']}):** {result['text']}")
                        # AUTOPLAY BUG FIXED HERE:
                        st.audio(result["audio_buffer"], format="audio/mp3") 
                    else:
                        st.error(result["error"])
            else:
                st.info("Route calculation complete. No further turns required.")
        else:
            st.info("⚠️ Please load the map in the Corporate Dashboard first to generate the route data.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tele:
        st.markdown(
            """
            <div class="section-card">
                <h4>📡 Vehicle Telemetry</h4>
                <p><strong>Speed:</strong> — km/h</p>
                <p><strong>Engine temp:</strong> — °C</p>
                <p><strong>Load weight:</strong> — kg</p>
                <div class="placeholder-block" style="height:40px; display:flex; align-items:center; justify-content:center;">
                    Live OBD feed — Phase 2
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    """
    <hr style="border:none; border-top:1px solid #DDD8CD; margin-top:32px;">
    <p style="text-align:center; color:#B0A890; font-size:0.75rem; padding-bottom:12px;">
        Agri-Logistics IDAS &nbsp;·&nbsp; Phase 1 Prototype &nbsp;·&nbsp;
        Sindh Agricultural Supply Chain &nbsp;·&nbsp; 2024
    </p>
    """,
    unsafe_allow_html=True,
)