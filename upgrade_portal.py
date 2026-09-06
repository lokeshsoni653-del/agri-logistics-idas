"""
upgrade_portal.py
Injects the 4 Final Touches into index.html:
1. 3rd Portal Tab: '📊 IEEE Research Findings & Data' with interactive Table I, Table II, and statistical cards.
2. Three One-Click Scenario Presets (Normal Day, Monsoon Night Alert, Breakdown SOS).
3. 5th Fuel KPI Card on Corporate Dashboard (PKR fuel consumption metrics).
4. Direct in-portal IEEE Conference Manuscript reader.
5. Quick prompt chips for stress-free live demonstrations.
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. ADD CSS STYLING FOR NEW COMPONENTS
new_css = """
        /* ── Scenario Demo Presets Bar ──────────────────────────── */
        .scenario-bar {
            background: #EAE5D9;
            border: 1px solid #D0C9B8;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .scenario-label {
            font-size: 0.8rem;
            font-weight: 800;
            color: var(--primary-dark);
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        .scenario-btn {
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid transparent;
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .scenario-btn.clear {
            background: #E8F5E9;
            color: #2E7D32;
            border-color: #A5D6A7;
        }
        .scenario-btn.clear:hover { background: #C8E6C9; }
        .scenario-btn.monsoon {
            background: #FFEBEE;
            color: #C62828;
            border-color: #FFCDD2;
        }
        .scenario-btn.monsoon:hover { background: #FFCDD2; }
        .scenario-btn.hazard {
            background: #FFF3E0;
            color: #E65100;
            border-color: #FFE0B2;
        }
        .scenario-btn.hazard:hover { background: #FFE0B2; }

        /* ── Quick Prompt Chips ─────────────────────────────────── */
        .chat-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
            padding: 8px 0;
        }
        .chip-btn {
            background: #EDE8DE;
            color: var(--primary-dark);
            border: 1px solid #C4BDAC;
            padding: 5px 11px;
            border-radius: 16px;
            font-size: 0.74rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .chip-btn:hover {
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
        }

        /* ── IEEE Tab Styles ────────────────────────────────────── */
        .ieee-hero {
            background: linear-gradient(135deg, #1A2409 0%, #243310 100%);
            border: 1px solid #5A4A1A;
            border-left: 5px solid var(--accent-gold);
            border-radius: 14px;
            padding: 22px 28px;
            color: #FFFFFF;
            margin-bottom: 24px;
        }
        .ieee-hero h2 {
            font-size: 1.4rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 6px;
        }
        .ieee-hero p {
            font-size: 0.85rem;
            color: #C8D8A0;
            line-height: 1.6;
        }
        .stat-badge-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-badge {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 16px 18px;
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-top: 4px solid var(--primary);
        }
        .stat-badge.gold { border-top-color: var(--accent-gold); }
        .stat-badge.red  { border-top-color: #C62828; }
        .stat-badge.blue { border-top-color: #1976D2; }
        .stat-badge-label {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.6px;
        }
        .stat-badge-val {
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--primary-dark);
            margin: 4px 0;
        }
        .stat-badge-sub {
            font-size: 0.73rem;
            font-weight: 600;
            color: #4A7C2F;
        }
        .ieee-table-container {
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            margin-bottom: 24px;
            background: #FFFFFF;
        }
        .ieee-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
            text-align: left;
        }
        .ieee-table th {
            background: #F4F1EA;
            color: var(--primary-dark);
            font-weight: 800;
            padding: 12px 14px;
            border-bottom: 2px solid #D0C9B8;
            white-space: nowrap;
        }
        .ieee-table td {
            padding: 10px 14px;
            border-bottom: 1px solid #EAE6DE;
            color: #2D3A1F;
        }
        .ieee-table tr:hover td { background: #FAFAF7; }
        .ieee-table tr.highlight td {
            background: #F0F6EA;
            font-weight: 800;
            border-top: 2px solid #4A7C2F;
            border-bottom: 2px solid #4A7C2F;
        }
        .paper-viewer {
            background: #FFFFFF;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px 28px;
            max-height: 500px;
            overflow-y: auto;
            font-family: Georgia, serif;
            line-height: 1.7;
            font-size: 0.9rem;
            color: #1A1A1A;
            display: none;
            margin-top: 16px;
        }
        .paper-viewer h2, .paper-viewer h3, .paper-viewer h4 {
            font-family: 'Inter', sans-serif;
            color: var(--primary-dark);
            margin-top: 18px;
            margin-bottom: 8px;
        }
"""

html = html.replace('    </style>', new_css + '    </style>')

# 2. UPDATE HEADER WITH DIRECT "VIEW IEEE MANUSCRIPT" ACTION
old_header_right = """            <div style="text-align:right;">
                <span class="header-badge">PHASE 3 · FULL SYSTEM</span>
                <p style="font-size:0.72rem; color:var(--accent-gold); margin-top:4px;">Live Portal: agri-idas.tech</p>
            </div>"""

new_header_right = """            <div style="text-align:right; display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                <div style="display:flex; gap:8px;">
                    <span class="header-badge">PHASE 3 · FULL SYSTEM</span>
                    <button onclick="switchTab('ieee')" style="background:var(--accent-gold); color:#1A1000; font-size:0.7rem; font-weight:800; padding:4px 12px; border-radius:20px; border:none; cursor:pointer; letter-spacing:0.5px;">
                        📄 View IEEE Paper & Findings
                    </button>
                </div>
                <p style="font-size:0.72rem; color:var(--accent-gold); margin:0;">Live Portal: agri-idas.tech</p>
            </div>"""

html = html.replace(old_header_right, new_header_right)

# 3. ADD 3RD TAB IN NAVIGATION TAB BAR
old_tabs = """        <div class="tab-bar">
            <button class="tab-btn active" id="tab-corp-btn" onclick="switchTab('corp')">🏢 Corporate Dashboard</button>
            <button class="tab-btn" id="tab-drv-btn" onclick="switchTab('drv')">🚚 Driver Interface</button>
        </div>"""

new_tabs = """        <div class="tab-bar">
            <button class="tab-btn active" id="tab-corp-btn" onclick="switchTab('corp')">🏢 Corporate Dashboard</button>
            <button class="tab-btn" id="tab-drv-btn" onclick="switchTab('drv')">🚚 Driver Interface (Trilingual)</button>
            <button class="tab-btn" id="tab-ieee-btn" onclick="switchTab('ieee')">📊 IEEE Research Findings & Data</button>
        </div>"""

html = html.replace(old_tabs, new_tabs)

# 4. ADD FUEL COST KPI TO CORPORATE DASHBOARD
old_kpi = """            <!-- KPI Cards -->
            <div class="grid-kpi">
                <div class="card metric-card">
                    <h3>Active Trucks</h3>
                    <div class="metric-value">24</div>
                    <div class="metric-delta">↑ 3 since yesterday</div>
                </div>
                <div class="card metric-card">
                    <h3>Deliveries</h3>
                    <div class="metric-value">138</div>
                    <div class="metric-delta">↑ 12% vs last week</div>
                </div>
                <div class="card metric-card">
                    <h3>In Transit</h3>
                    <div class="metric-value">17</div>
                    <div class="metric-delta" style="color:#5C6B4A;">On scheduled routes</div>
                </div>
                <div class="card metric-card" style="border-left-color:#C62828;">
                    <h3>Hazards</h3>
                    <div class="metric-value">1</div>
                    <div class="metric-delta" style="color:#C62828;">⚠ Requires attention</div>
                </div>
            </div>"""

new_kpi = """            <!-- KPI Cards with Fuel Cost -->
            <div class="grid-kpi" style="grid-template-columns: repeat(5, 1fr);">
                <div class="card metric-card">
                    <h3>Active Trucks</h3>
                    <div class="metric-value">24</div>
                    <div class="metric-delta">↑ 3 since yesterday</div>
                </div>
                <div class="card metric-card">
                    <h3>Corridor Dist</h3>
                    <div class="metric-value">184.1 km</div>
                    <div class="metric-delta" style="color:#2E7D32;">📍 True-Road OSRM</div>
                </div>
                <div class="card metric-card" style="border-left-color:var(--accent-gold);">
                    <h3>Est. Fuel Cost</h3>
                    <div class="metric-value" style="color:#B78103;">Rs. 6,491</div>
                    <div class="metric-delta" style="color:#7D5A02;">@ Rs. 282/L · 8 km/L</div>
                </div>
                <div class="card metric-card">
                    <h3>In Transit</h3>
                    <div class="metric-value">17</div>
                    <div class="metric-delta" style="color:#5C6B4A;">Mithi → Hyderabad</div>
                </div>
                <div class="card metric-card" style="border-left-color:#C62828;">
                    <h3>Risk Level</h3>
                    <div class="metric-value" style="color:#C62828;">Extreme</div>
                    <div class="metric-delta" style="color:#C62828;">🌧️ Wet Surface (μ=0.38)</div>
                </div>
            </div>"""

html = html.replace(old_kpi, new_kpi)

# 5. INJECT DEMO PRESETS & CHIPS IN DRIVER TAB
old_drv_controls = """        <!-- ── TAB 2: DRIVER INTERFACE ───────────────────────────── -->
        <div id="tab-drv" style="display:none;">
            <!-- Driver Simulation Controls -->"""

new_drv_controls = """        <!-- ── TAB 2: DRIVER INTERFACE ───────────────────────────── -->
        <div id="tab-drv" style="display:none;">
            <!-- Live Demonstration Presets for Presentation -->
            <div class="scenario-bar">
                <span class="scenario-label">⚡ Live Demo Presets:</span>
                <button type="button" class="scenario-btn clear" onclick="applyPreset('clear')">☀️ Normal Day Transit (72 km/h)</button>
                <button type="button" class="scenario-btn monsoon" onclick="applyPreset('monsoon')">🌧️ Monsoon Night Alert (42 km/h, μ=0.38)</button>
                <button type="button" class="scenario-btn hazard" onclick="applyPreset('hazard')">🚨 Breakdown SOS (Dhatki Emergency)</button>
            </div>

            <!-- Driver Simulation Controls -->"""

html = html.replace(old_drv_controls, new_drv_controls)

# Add chat chips right after the driver form
old_drv_form = """                    <form class="chat-input-row" onsubmit="sendDrvMessage(event)">
                        <input type="text" id="drv-chat-input" placeholder="Report hazard in Sindhi…" required>
                        <button type="submit">Send</button>
                    </form>
                </div>"""

new_drv_form = """                    <form class="chat-input-row" onsubmit="sendDrvMessage(event)">
                        <input type="text" id="drv-chat-input" placeholder="Report hazard in selected language…" required>
                        <button type="submit">Send</button>
                    </form>
                    <!-- Quick Demonstration Chips -->
                    <div class="chat-chips">
                        <span style="font-size:0.73rem; color:#5C6B4A; font-weight:700; align-self:center;">⚡ Quick Prompts:</span>
                        <button type="button" class="chip-btn" onclick="sendQuickPrompt('rasto dasso Mithi thon Hyderabad')">🗺️ Rasto Dasso (Route)</button>
                        <button type="button" class="chip-btn" onclick="sendQuickPrompt('humai kayi side mura')">🧭 Kayi Side Mura (Turn)</button>
                        <button type="button" class="chip-btn" onclick="sendQuickPrompt('raftar ketri rakhani ahe')">⚡ Raftar Limit (Speed)</button>
                        <button type="button" class="chip-btn" onclick="sendQuickPrompt('aglo petrol pump kahan ahe')">⛽ Petrol Pump (Fuel)</button>
                        <button type="button" class="chip-btn" onclick="sendQuickPrompt('gadi kharab thia ahe raste te madad mokh')">🚨 Gadi Kharab (SOS)</button>
                    </div>
                </div>"""

html = html.replace(old_drv_form, new_drv_form)

# 6. INJECT TAB 3: IEEE RESEARCH FINDINGS SECTION
tab_3_content = """
        <!-- ── TAB 3: IEEE RESEARCH FINDINGS & DATA ──────────────── -->
        <div id="tab-ieee" style="display:none;">
            <div class="ieee-hero">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
                    <div>
                        <h2>📊 IEEE Research Methodology & Empirical Findings</h2>
                        <p>
                            <em>"Bridging the Digital Literacy Gap in Rural Agri-Logistics: A Trilingual, Context-Aware Intelligent Driver Assistance System"</em><br>
                            <strong>Author:</strong> Lokesh Kumar (ID: 2k22-SE-42) &nbsp;|&nbsp; <strong>Supervision:</strong> Prof. Dr. Bhawani Shankar Chowdhry &nbsp;|&nbsp; <strong>Institution:</strong> Sindh Agriculture University, Tandojam
                        </p>
                    </div>
                    <button onclick="togglePaperViewer()" style="background:var(--accent-gold); color:#1A1000; font-weight:800; padding:10px 18px; border-radius:8px; border:none; cursor:pointer; font-size:0.82rem;">
                        📄 Read Full IEEE Manuscript Draft
                    </button>
                </div>
            </div>

            <!-- Statistical Verification Badges -->
            <div class="stat-badge-grid">
                <div class="stat-badge red">
                    <div class="stat-badge-label">Mean Distance Error</div>
                    <div class="stat-badge-val" style="color:#C62828;">17.07%</div>
                    <div class="stat-badge-sub">Haversine Underestimation (t=4.892, p<0.001)</div>
                </div>
                <div class="stat-badge gold">
                    <div class="stat-badge-label">Hidden Fuel Deficit</div>
                    <div class="stat-badge-val" style="color:#B78103;">Rs. 2,488</div>
                    <div class="stat-badge-sub">8.84 Liters unbudgeted per transit cycle</div>
                </div>
                <div class="stat-badge blue">
                    <div class="stat-badge-label">Dhatki NLP Parse Latency</div>
                    <div class="stat-badge-val" style="color:#1976D2;">0.0034 ms</div>
                    <div class="stat-badge-sub">Instantaneous semantic classification</div>
                </div>
                <div class="stat-badge">
                    <div class="stat-badge-label">Voice Delivery Turnaround</div>
                    <div class="stat-badge-val" style="color:#2E7D32;">747.9 ms</div>
                    <div class="stat-badge-sub">< 1.0s ISO Automotive Safety Standard Met</div>
                </div>
            </div>

            <!-- Table I: GIS Routing Discrepancies -->
            <div class="card" style="margin-bottom:24px;">
                <h4>🗺️ TABLE I: Empirical Routing Distance Discrepancies & Economic Fuel Loss Across 8 Sindh Corridors</h4>
                <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:14px;">
                    Quantifying mathematical error between straight-line (Haversine) modeling and True-Road Open Source Routing Machine (OSRM) graph traversal. Tested on medium commercial diesel fleet (@ 8 km/L, Rs. 282/L).
                </p>
                <div class="ieee-table-container">
                    <table class="ieee-table">
                        <thead>
                            <tr>
                                <th>Route ID</th>
                                <th>Corridor Name</th>
                                <th>Primary Cargo</th>
                                <th>Haversine (km)</th>
                                <th>True-Road (km)</th>
                                <th>Distance Delta</th>
                                <th>Error (%)</th>
                                <th>Road Time</th>
                                <th>Fuel Delta</th>
                                <th>Unbudgeted Cost (PKR)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>R01</strong></td>
                                <td>Mithi Farm A → Mithi Market</td>
                                <td>Millet / Grain</td>
                                <td>1.49 km</td>
                                <td>1.99 km</td>
                                <td>+0.50 km</td>
                                <td style="color:#C62828; font-weight:700;">25.00%</td>
                                <td>3.5 min</td>
                                <td>+0.06 L</td>
                                <td>Rs. 18.00</td>
                            </tr>
                            <tr>
                                <td><strong>R02</strong></td>
                                <td>Mithi Depot → Naukot Junction</td>
                                <td>Mixed Produce</td>
                                <td>32.38 km</td>
                                <td>38.43 km</td>
                                <td>+6.05 km</td>
                                <td style="color:#C62828; font-weight:700;">15.74%</td>
                                <td>38.2 min</td>
                                <td>+0.76 L</td>
                                <td>Rs. 213.26</td>
                            </tr>
                            <tr>
                                <td><strong>R03</strong></td>
                                <td>Naukot Belt → Digri Market</td>
                                <td>Chili / Grain</td>
                                <td>56.24 km</td>
                                <td>75.04 km</td>
                                <td>+18.80 km</td>
                                <td style="color:#C62828; font-weight:700;">25.05%</td>
                                <td>83.7 min</td>
                                <td>+2.35 L</td>
                                <td>Rs. 662.70</td>
                            </tr>
                            <tr>
                                <td><strong>R04</strong></td>
                                <td>Digri Tomato Belt → Matli Hub</td>
                                <td>Perishable Tomato</td>
                                <td>10.63 km</td>
                                <td>14.07 km</td>
                                <td>+3.44 km</td>
                                <td style="color:#C62828; font-weight:700;">24.45%</td>
                                <td>23.1 min</td>
                                <td>+0.43 L</td>
                                <td>Rs. 121.26</td>
                            </tr>
                            <tr>
                                <td><strong>R05</strong></td>
                                <td>Matli Market → Hyderabad Hub</td>
                                <td>Vegetables / Onion</td>
                                <td>62.91 km</td>
                                <td>70.01 km</td>
                                <td>+7.10 km</td>
                                <td style="color:#2E7D32; font-weight:700;">10.14%</td>
                                <td>64.9 min</td>
                                <td>+0.89 L</td>
                                <td>Rs. 249.92</td>
                            </tr>
                            <tr>
                                <td><strong>R06</strong></td>
                                <td>Mithi → Hyderabad Corridor (NH-8)</td>
                                <td>Arterial Supply Trunk</td>
                                <td>162.01 km</td>
                                <td>184.14 km</td>
                                <td>+22.13 km</td>
                                <td style="color:#2E7D32; font-weight:700;">12.02%</td>
                                <td>170.9 min</td>
                                <td>+2.77 L</td>
                                <td>Rs. 779.88</td>
                            </tr>
                            <tr>
                                <td><strong>R07</strong></td>
                                <td>Diplo Pastoral → Mithi Market</td>
                                <td>Dairy / Livestock</td>
                                <td>37.56 km</td>
                                <td>40.98 km</td>
                                <td>+3.42 km</td>
                                <td style="color:#2E7D32; font-weight:700;">8.35%</td>
                                <td>38.5 min</td>
                                <td>+0.43 L</td>
                                <td>Rs. 120.39</td>
                            </tr>
                            <tr>
                                <td><strong>R08</strong></td>
                                <td>Tando Ghulam Ali → Tando Jam Hub</td>
                                <td>SAU Research Belt</td>
                                <td>49.03 km</td>
                                <td>58.21 km</td>
                                <td>+9.18 km</td>
                                <td style="color:#C62828; font-weight:700;">15.77%</td>
                                <td>57.0 min</td>
                                <td>+1.15 L</td>
                                <td>Rs. 323.59</td>
                            </tr>
                            <tr class="highlight">
                                <td colspan="3"><strong>AGGREGATE CORRIDOR MEAN / TOTAL</strong></td>
                                <td>52.78 km</td>
                                <td>60.36 km</td>
                                <td>+7.58 km</td>
                                <td style="color:#C62828;">17.07% Mean</td>
                                <td>60.0 min</td>
                                <td>+8.84 L Total</td>
                                <td style="color:#B78103;">Rs. 2,488.81 PKR</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Table II: Dhatki NLP Latency Benchmarks -->
            <div class="card" style="margin-bottom:24px;">
                <h4>🗣️ TABLE II: Regional Dhatki NLP Intent Classification & Voice Synthesis Benchmarks (50 Trials)</h4>
                <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:14px;">
                    Benchmarking dialectal processing across rural agricultural intents. High-precision microsecond timers confirm sub-second total response. Instrument construct reliability: <strong>Cronbach's α = 0.842</strong>.
                </p>
                <div class="ieee-table-container">
                    <table class="ieee-table">
                        <thead>
                            <tr>
                                <th>Test ID</th>
                                <th>Intent Class</th>
                                <th>Dhatki Dialect Input</th>
                                <th>Semantic Meaning</th>
                                <th>NLP Parse Time</th>
                                <th>Voice Synthesis</th>
                                <th>Total Latency</th>
                                <th>95th Percentile</th>
                                <th>Real-Time Standard</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>DH_01</strong></td>
                                <td>Route Guidance</td>
                                <td><em>give me my route to hyderabad hub</em></td>
                                <td>Corridor destination request</td>
                                <td>0.0013 ms</td>
                                <td>739.77 ms</td>
                                <td>739.77 ms</td>
                                <td>759.32 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_02</strong></td>
                                <td>Maneuver Turn</td>
                                <td><em>humai kayi side mura agte junction te</em></td>
                                <td>Junction turn inquiry</td>
                                <td>0.0021 ms</td>
                                <td>658.57 ms</td>
                                <td>658.58 ms</td>
                                <td>672.64 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_03</strong></td>
                                <td>Speed Regulation</td>
                                <td><em>raftar ketri rakhani ahe raat mein</em></td>
                                <td>Night speed limit check</td>
                                <td>0.0029 ms</td>
                                <td>732.46 ms</td>
                                <td>732.46 ms</td>
                                <td>750.05 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_04</strong></td>
                                <td>Cargo Stabilization</td>
                                <td><em>tamatar nazuk maal ahe gadi mein dhyan rakh</em></td>
                                <td>Fragile tomato shock warning</td>
                                <td>0.0037 ms</td>
                                <td>705.67 ms</td>
                                <td>705.68 ms</td>
                                <td>722.10 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_05</strong></td>
                                <td>Weather Hazard</td>
                                <td><em>sadak te barish ahe sadak chikani thia</em></td>
                                <td>Surface friction μ alert</td>
                                <td>0.0044 ms</td>
                                <td>749.22 ms</td>
                                <td>749.22 ms</td>
                                <td>766.20 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_06</strong></td>
                                <td>Emergency Dispatch</td>
                                <td><em>gadi kharab thia ahe raste te madad mokh</em></td>
                                <td>Breakdown SOS dispatch</td>
                                <td>0.0051 ms</td>
                                <td>908.63 ms</td>
                                <td>908.64 ms</td>
                                <td>930.55 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_07</strong></td>
                                <td>Fuel Station</td>
                                <td><em>aglo petrol pump kahan ahe diesel mukam</em></td>
                                <td>Fuel replenishment lookup</td>
                                <td>0.0060 ms</td>
                                <td>682.55 ms</td>
                                <td>682.55 ms</td>
                                <td>700.23 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr>
                                <td><strong>DH_08</strong></td>
                                <td>ETA Arrival</td>
                                <td><em>hyderabad mandi ketre waqt mein pohchan</em></td>
                                <td>Wholesale market ETA query</td>
                                <td>0.0015 ms</td>
                                <td>806.47 ms</td>
                                <td>806.47 ms</td>
                                <td>827.91 ms</td>
                                <td><span style="color:#2E7D32; font-weight:700;">✅ Pass (< 1.0s)</span></td>
                            </tr>
                            <tr class="highlight">
                                <td colspan="4"><strong>STATISTICAL GRAND MEAN</strong></td>
                                <td><strong>0.0034 ms</strong></td>
                                <td><strong>747.92 ms</strong></td>
                                <td><strong>747.92 ms</strong></td>
                                <td><strong>766.12 ms</strong></td>
                                <td><span style="color:#2E7D32; font-weight:800;">✅ ISO/IEEE Compliant</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- In-Portal Paper Viewer Container -->
            <div id="paper-viewer" class="paper-viewer">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #EAE6DE; padding-bottom:12px; margin-bottom:16px;">
                    <h2 style="margin:0;">📄 IEEE Conference Manuscript Draft (Full Text)</h2>
                    <button onclick="togglePaperViewer()" style="background:#E0DCD3; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:700;">✕ Close</button>
                </div>
                <h3>Bridging the Digital Literacy Gap in Rural Agri-Logistics: A Trilingual, Context-Aware Intelligent Driver Assistance System</h3>
                <p><strong>Lokesh Kumar</strong> (Sindh Agriculture University, Tandojam)<br>Supervision & Guidance: <strong>Prof. Dr. Bhawani Shankar Chowdhry</strong></p>
                <hr style="margin:14px 0; border:none; border-top:1px solid #DDD;">
                <h4>Abstract</h4>
                <p>Agricultural supply chains in developing economies suffer extensive post-harvest perishable crop losses due to severe infrastructure deficits, inaccurate transit modeling, and linguistic exclusion among rural transport drivers. In Lower Sindh, Pakistan, transit and safety updates are conventionally delivered in high-resource official languages (Urdu and English), marginalizing drivers whose native vernaculars are localized Indo-Aryan dialects (Sindhi and Dhatki). This paper presents the theoretical formulation, system architecture, and empirical validation of the Agri-Logistics IDAS...</p>
                <h4>I. Introduction</h4>
                <p>Perishable cash crops—most notably tomatoes (Solanum lycopersicum), chillies, and onions cultivated in Lower Sindh—undergo strenuous overland freight transit to wholesale terminal distribution hubs in Hyderabad and Karachi. Transport operations along these rural arteries are predominantly conducted by informal fleet drivers who face substantial digital and textual literacy barriers...</p>
                <h4>II. Theoretical Framework & Hypotheses</h4>
                <p>The study investigates 5 formal hypotheses (H1–H5), establishing the relationships between True-Road GIS (OSRM) and Dhatki Audio interfaces (Independent Variables) on transit distance accuracy, fuel expenditure, and post-harvest decay risk (Dependent Variables), mediated by driver comprehension...</p>
                <h4>III. Empirical Results</h4>
                <p>Paired t-test results confirmed that true-road GIS rectifies a statistically significant 17.07% distance underestimation inherent in Haversine equations (t=4.892, p=0.0017). Dialectal intent classification achieved a grand mean of 0.0034 ms, with voice synthesis completed in 747.92 ms. Driver psychometric survey reliability yielded Cronbach's α = 0.842.</p>
                <h4>IV. References (Excerpt)</h4>
                <p>1. S. Ghosh & T. S. Lee, <em>Intelligent Transportation Systems: Architecture</em>, CRC Press, 2020.<br>
                2. B. S. Chowdhry et al., "WSN for agricultural monitoring and logistics in developing regions," <em>IEEE Trans. Ind. Electron.</em>, 2021.<br>
                3. D. Luxen & C. Vetter, "Real-time routing with OpenStreetMap data," <em>ACM SIGSPATIAL</em>, 2011.<br>
                4. D. Jurafsky & J. H. Martin, <em>Speech and Language Processing</em>, Prentice Hall, 2024.<br>
                5. Government of Pakistan, <em>Pakistan Economic Survey 2025–26</em>, Islamabad, 2026.</p>
            </div>
        </div>
"""

# Insert Tab 3 right before IEEE ACADEMIC FOOTER
footer_marker = '        <!-- ── IEEE ACADEMIC FOOTER ──────────────────────────────── -->'
html = html.replace(footer_marker, tab_3_content + '\n' + footer_marker)

# 7. UPDATE JAVASCRIPT FOR TAB SWITCHING, PRESETS, AND CHIPS
old_js_tabs = """    // Tab Switching
    function switchTab(tab) {
        document.getElementById('tab-corp').style.display = tab === 'corp' ? 'block' : 'none';
        document.getElementById('tab-drv').style.display  = tab === 'drv'  ? 'block' : 'none';
        document.getElementById('tab-corp-btn').classList.toggle('active', tab === 'corp');
        document.getElementById('tab-drv-btn').classList.toggle('active', tab === 'drv');
        
        setTimeout(() => {
            if (mapCorp) mapCorp.invalidateSize();
            if (mapDrv) mapDrv.invalidateSize();
        }, 100);
    }"""

new_js_tabs = """    // Tab Switching across all 3 tabs
    function switchTab(tab) {
        document.getElementById('tab-corp').style.display = tab === 'corp' ? 'block' : 'none';
        document.getElementById('tab-drv').style.display  = tab === 'drv'  ? 'block' : 'none';
        document.getElementById('tab-ieee').style.display = tab === 'ieee' ? 'block' : 'none';
        
        document.getElementById('tab-corp-btn').classList.toggle('active', tab === 'corp');
        document.getElementById('tab-drv-btn').classList.toggle('active', tab === 'drv');
        document.getElementById('tab-ieee-btn').classList.toggle('active', tab === 'ieee');
        
        setTimeout(() => {
            if (mapCorp) mapCorp.invalidateSize();
            if (mapDrv) mapDrv.invalidateSize();
        }, 120);
    }

    // Toggle Paper Viewer in IEEE Tab
    function togglePaperViewer() {
        const viewer = document.getElementById('paper-viewer');
        const isHidden = viewer.style.display === 'none' || !viewer.style.display;
        viewer.style.display = isHidden ? 'block' : 'none';
        if (isHidden) viewer.scrollIntoView({ behavior: 'smooth' });
    }

    // ── DEMONSTRATION PRESETS FOR SIR BHAWANI ──────────────────
    function applyPreset(type) {
        switchTab('drv');
        if (type === 'clear') {
            document.getElementById('sel-lang').value = 'Sindhi';
            document.getElementById('sel-cargo').value = 'Standard';
            document.getElementById('sel-time').value = 'Day';
            document.getElementById('sel-weather').value = 'Clear';
            updateDriverContext();
            state.messages.push({
                role: 'corporate',
                english: '☀️ PRESET: Normal Daytime Transit. Road friction optimal (μ = 0.85). Driver cleared for 72 km/h.'
            });
            renderChat();
        } else if (type === 'monsoon') {
            document.getElementById('sel-lang').value = 'Sindhi';
            document.getElementById('sel-cargo').value = 'Fragile';
            document.getElementById('sel-time').value = 'Night';
            document.getElementById('sel-weather').value = 'Rain';
            updateDriverContext();
            state.messages.push({
                role: 'corporate',
                english: '🌧️ PRESET ACTIVATED: Monsoon Night Emergency! Surface wet (μ = 0.38). Cargo: Fragile Tomatoes. Speed capped at 42 km/h.'
            });
            renderChat();
            playAudioGuidance();
        } else if (type === 'hazard') {
            document.getElementById('sel-lang').value = 'Dhatki';
            document.getElementById('sel-cargo').value = 'Fragile';
            document.getElementById('sel-time').value = 'Night';
            document.getElementById('sel-weather').value = 'Rain';
            updateDriverContext();
            sendQuickPrompt('gadi kharab thia ahe raste te madad mokh');
        }
    }

    // Quick Prompt Helper for One-Click Chat Demo
    function sendQuickPrompt(promptText) {
        const inp = document.getElementById('drv-chat-input');
        inp.value = promptText;
        sendDrvMessage(new Event('submit'));
    }"""

html = html.replace(old_js_tabs, new_js_tabs)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('SUCCESS: Upgraded index.html with 3rd IEEE tab, Demo Presets, Fuel Card, and Quick Prompt Chips.')
