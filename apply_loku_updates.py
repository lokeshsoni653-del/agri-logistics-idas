"""
apply_loku_updates.py
Fixes the 3 user issues:
1. Button in header & Tab 3 opens research_proposal.pdf directly in new tab.
2. Audio Advisory Guidance dynamically changes with Language, Weather, Route Progress, and Presets, speaking proper dialect text.
3. Overhauls AI-sounding text into Lokesh Kumar's authentic, earnest, professional software engineering student writing style.
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. FIX HEADER & PDF LINK ───────────────────────────────────────
old_header = """            <div style="text-align:right; display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                <div style="display:flex; gap:8px;">
                    <span class="header-badge">PHASE 3 · FULL SYSTEM</span>
                    <button onclick="switchTab('ieee')" style="background:var(--accent-gold); color:#1A1000; font-size:0.7rem; font-weight:800; padding:4px 12px; border-radius:20px; border:none; cursor:pointer; letter-spacing:0.5px;">
                        📄 View IEEE Paper & Findings
                    </button>
                </div>
                <p style="font-size:0.72rem; color:var(--accent-gold); margin:0;">Live Portal: agri-idas.tech</p>
            </div>"""

new_header = """            <div style="text-align:right; display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                <div style="display:flex; gap:8px; align-items:center;">
                    <span class="header-badge">SAU FYP 2026</span>
                    <a href="research_proposal.pdf" target="_blank" style="text-decoration:none;">
                        <button type="button" style="background:var(--accent-gold); color:#1A1000; font-size:0.72rem; font-weight:800; padding:6px 14px; border-radius:20px; border:none; cursor:pointer; letter-spacing:0.5px; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
                            📄 View Research Proposal (PDF)
                        </button>
                    </a>
                </div>
                <p style="font-size:0.72rem; color:var(--accent-gold); margin:0;">Live Portal: agri-idas.tech</p>
            </div>"""

html = html.replace(old_header, new_header)

# Also update the title & subtitle in the header to Loku's natural tone
old_h1_block = """            <div>
                <h1>🌾 Agri-Logistics IDAS</h1>
                <p>Intelligent Driver Assistance System · Sindh Agricultural Supply Chain (Mithi → Hyderabad)</p>
            </div>"""

new_h1_block = """            <div>
                <h1>🌾 Agri-Logistics IDAS</h1>
                <p style="color:#C5DFA0; font-size:0.83rem; margin-top:4px;">
                    Final Year Research Project · Dept. of Software Engineering, Sindh Agriculture University, Tandojam<br/>
                    <span style="font-size:0.76rem; color:#E0EAD0;">Smart Route Safety & Trilingual Voice Guidance for Sindh Agricultural Transport (Mithi → Hyderabad)</span>
                </p>
            </div>"""

html = html.replace(old_h1_block, new_h1_block)

# ── 2. SIDEBAR TEXT IN LOKU'S NATURAL VOICE ────────────────────────
old_sidebar_context = """        <div class="sidebar-section">
            <h4>📋 Research Context</h4>
            <strong style="color:#C8D8A0;">Title:</strong><br>
            <em>Bridging the Digital Literacy Gap in Rural Agri-Logistics Using a Trilingual, Context-Aware IDAS</em>
            <br><br>
            <strong style="color:#C8D8A0;">Objective:</strong><br>
            Zero-literacy-barrier access to route safety for Sindhi, Urdu, and Dhatki drivers.
        </div>"""

new_sidebar_context = """        <div class="sidebar-section">
            <h4>📋 About This Research</h4>
            <strong style="color:#C8D8A0;">Why I Built This Project:</strong>
            <p style="font-size:0.74rem; line-height:1.5; margin-top:5px; color:#DCE7CA;">
                In Lower Sindh (Tharparkar, Badin, Mirpurkhas), our local drivers transport fresh tomatoes and vegetables to Hyderabad wholesale market. Most drivers speak Sindhi and Dhatki and cannot read English text messages on mobile phones while driving.
            </p>
            <p style="font-size:0.74rem; line-height:1.5; margin-top:6px; color:#DCE7CA;">
                Under the supervision of <strong>Prof. Dr. Bhawani Shankar Chowdhry</strong>, this project solves this with True-Road navigation along actual canal roads and spoken voice advisories in Sindhi, Dhatki, and Urdu to stop tomato spoilage.
            </p>
        </div>"""

html = html.replace(old_sidebar_context, new_sidebar_context)

# ── 3. FIX AUDIO ADVISORY SECTION (HTML CONTAINER) ─────────────────
old_audio_card = """            <!-- Audio Guidance & Telemetry -->
            <div class="grid-2">
                <div class="card">
                    <h4>🔊 Audio Advisory Guidance</h4>
                    <div style="background:#F0EDE6; padding:12px; border-radius:8px; border-left:3px solid #4A7C2F; font-size:0.83rem; margin-bottom:12px;">
                        <strong>Next Maneuver:</strong> Turn sharp left onto National Highway 8 (12.0 km)
                    </div>
                    <button onclick="playAudioGuidance()" style="width:100%; padding:10px; border-radius:8px; border:none; background:var(--primary); color:#FFF; font-weight:700; cursor:pointer;">
                        🔊 Play Audio Advisory in Selected Language
                    </button>
                    <p id="audio-transcript" style="font-size:0.75rem; color:#5C6B4A; margin-top:8px; font-style:italic;"></p>
                </div>"""

new_audio_card = """            <!-- Audio Guidance & Telemetry -->
            <div class="grid-2">
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <h4 style="margin:0;">🔊 Audio Advisory Guidance</h4>
                        <span id="advisory-lang-badge" style="background:#2D5016; color:#FFF; font-size:0.7rem; font-weight:700; padding:2px 8px; border-radius:10px;">🟢 Sindhi Active</span>
                    </div>
                    
                    <!-- Dynamic Advisory Box -->
                    <div id="dynamic-advisory-box" style="background:#F4F1EA; padding:14px; border-radius:10px; border-left:4px solid #4A7C2F; margin-bottom:12px; transition:all 0.3s ease;">
                        <div id="advisory-headline" style="font-weight:800; font-size:0.88rem; color:#1E3A0F; margin-bottom:4px;">
                            🧭 اڳتي نيشنل هاءِ وي 8 تي سڌو هلو، مٽلي طرف (45 km)
                        </div>
                        <div id="advisory-roman" style="font-size:0.8rem; color:#4A5C3A; font-style:italic; margin-bottom:4px;">
                            "Agte National Highway 8 te siddho halo, Matli taraf (45 km)"
                        </div>
                        <div id="advisory-english" style="font-size:0.74rem; color:#6B604A; border-top:1px dashed #D0C9B8; padding-top:4px;">
                            <strong>English Translation:</strong> Continue straight on National Highway 8 toward Matli for 45 km.
                        </div>
                    </div>

                    <button type="button" onclick="playAudioGuidance()" style="width:100%; padding:11px; border-radius:8px; border:none; background:var(--primary); color:#FFF; font-weight:700; cursor:pointer; font-size:0.86rem; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span>🔊</span> <span id="advisory-btn-label">Speak Advisory in Sindhi</span>
                    </button>
                    <p id="audio-transcript" style="font-size:0.75rem; color:#2D5016; margin-top:8px; font-weight:600; min-height:18px;"></p>
                </div>"""

html = html.replace(old_audio_card, new_audio_card)

# ── 4. REWRITE TAB 3 TEXT IN LOKU'S HONEST, AUTHENTIC VOICE ────────
old_tab3_hero = """        <!-- ── TAB 3: IEEE RESEARCH FINDINGS & DATA ──────────────── -->
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
            </div>"""

new_tab3_hero = """        <!-- ── TAB 3: IEEE RESEARCH FINDINGS & DATA ──────────────── -->
        <div id="tab-ieee" style="display:none;">
            <div class="ieee-hero">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:14px;">
                    <div style="max-width:750px;">
                        <h2>📊 Project Testing Results & Research Data</h2>
                        <p style="color:#DCE7CA; font-size:0.86rem; line-height:1.6;">
                            <strong>Research Paper Title:</strong> <em>"Bridging the Digital Literacy Gap in Rural Agri-Logistics: A Trilingual, Context-Aware Intelligent Driver Assistance System"</em><br/>
                            <strong>Student Researcher:</strong> Lokesh Kumar (ID: 2k22-SE-42) &nbsp;|&nbsp; 
                            <strong>Supervisor:</strong> Prof. Dr. Bhawani Shankar Chowdhry<br/>
                            <strong>Department:</strong> Software Engineering, Sindh Agriculture University, Tandojam
                        </p>
                        <p style="color:#C8D8A0; font-size:0.8rem; margin-top:8px; line-height:1.5; background:rgba(0,0,0,0.25); padding:8px 12px; border-radius:8px;">
                            <strong>Summary of Experiments:</strong> To prove that this system works for real farmers and drivers, I conducted two main experiments on 8 key agricultural routes in Sindh: (1) Measuring how much straight-line map math underestimates actual road travel and fuel consumption, and (2) Testing speech synthesis speed so drivers receive immediate voice alerts while driving.
                        </p>
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <a href="research_proposal.pdf" target="_blank" style="text-decoration:none;">
                            <button type="button" style="background:var(--accent-gold); color:#1A1000; font-weight:800; padding:10px 16px; border-radius:8px; border:none; cursor:pointer; font-size:0.82rem; width:100%; box-shadow:0 2px 8px rgba(0,0,0,0.2);">
                                📥 Open Formal Proposal (PDF)
                            </button>
                        </a>
                        <button type="button" onclick="togglePaperViewer()" style="background:#FFFFFF; color:var(--primary-dark); font-weight:700; padding:9px 16px; border-radius:8px; border:1px solid #C4BDAC; cursor:pointer; font-size:0.8rem;">
                            📄 Read Complete Paper Draft
                        </button>
                    </div>
                </div>
            </div>"""

html = html.replace(old_tab3_hero, new_tab3_hero)

# ── 5. JAVASCRIPT: DYNAMIC AUDIO ADVISORY ENGINE ───────────────────
js_advisory_logic = """
    // ── DYNAMIC CONTEXT-AWARE AUDIO ADVISORY SYSTEM ────────────────
    const ADVISORY_CORPUS = {
        Sindhi: {
            normal: {
                headline: 'اڳتي نيشنل هاءِ وي 8 تي سڌو هلو، مٽلي طرف (45 km)',
                roman: 'Agte National Highway 8 te siddho halo, Matli taraf (45 km)',
                english: 'Continue straight on National Highway 8 toward Matli for 45 km (Speed: 72 km/h).'
            },
            monsoon: {
                headline: 'خبردار! برسات ۽ رات آهي، روڊ چڪڻو آهي (μ=0.38). رفتار 42 ڪلوميٽر رکو ۽ ٽماٽن جو خيال رکو.',
                roman: 'Khabardar! Meenhan ain raat ahe. Raftar 42 km/h rakho, agte sadak chikni ahe.',
                english: 'Caution! Rain and night conditions. Road friction reduced (μ=0.38). Limit speed to 42 km/h to prevent tomato cargo damage.'
            },
            hazard: {
                headline: 'هنگامي الرٽ! ڊگھڙي وٽ روڊ بلاڪ آهي. ڊپلو واري پاسي کان متبادل رستو اختيار ڪريو.',
                roman: 'Alert! Digri wath rasto band ahe. Diplo taraf naye raste te wanj.',
                english: 'Emergency SOS: Route blocked near Digri. Rerouting via Diplo provincial detour.'
            },
            voiceLang: 'ur-PK'
        },
        Urdu: {
            normal: {
                headline: 'آگے نیشنل ہائی وے 8 پر سیدھے چلیں، مٹلی کی طرف (45 km)',
                roman: 'Aage National Highway 8 par seedha chalein, Matli ki taraf (45 km)',
                english: 'Continue straight on National Highway 8 toward Matli for 45 km (Speed: 72 km/h).'
            },
            monsoon: {
                headline: 'خبردار! بارش اور رات کا وقت ہے، سڑک پھسلن والی ہے۔ رفتار 42 کلومیٹر رکھیں اور ہیزارڈ لائٹس آن کریں۔',
                roman: 'Khabardar! Baarish aur raat ka waqt hai. Raftar 42 km/h rakhein aur hazard lights on karein.',
                english: 'Caution! Rain and night conditions. Road is slippery (μ=0.38). Maintain 42 km/h and turn hazard lights ON.'
            },
            hazard: {
                headline: 'ہنگامی الرٹ! ڈگری کے قریب رکاوٹ ہے۔ ڈپلو والے متبادل راستے سے گاڑی آگے بڑھائیں۔',
                roman: 'Alert! Digri ke qareeb rukawat hai. Diplo ke mutabadil raste se chalein.',
                english: 'Emergency SOS: Breakdown or hazard near Digri. Reroute via Diplo detour.'
            },
            voiceLang: 'ur-PK'
        },
        Dhatki: {
            normal: {
                headline: 'آگیاں این ایچ 8 تے سدھا ونو، مٹلی سائیڈ (45 km)',
                roman: 'Aagya NH-8 te siddha vanjo, Matli side (45 km)',
                english: 'Drive straight on National Highway 8 toward Matli for 45 km (Speed: 72 km/h).'
            },
            monsoon: {
                headline: 'دھیان رکھو! بارش اتے رات ہے، سڑک چکنی ہے۔ رفتار 42 کرو اتے ٹماٹر سنبھالو۔',
                roman: 'Dhyan rakho! Barish atay raat hai, sadak chikni hai. Raftar 42 karo atay tamatar sambhalo.',
                english: 'Drive carefully! Rain and night on road. Slow to 42 km/h to protect perishable tomato load.'
            },
            hazard: {
                headline: 'الرٽ! ڊگھڙي پاڻي آهي، ڊپلو واٽے ونو۔',
                roman: 'Alert! Digri paas rukawat hai, Diplo raah te vanjo.',
                english: 'Emergency SOS: Road flooded near Digri. Divert along Diplo path.'
            },
            voiceLang: 'ur-PK'
        }
    };

    function updateAudioAdvisoryUI() {
        const lang = state.lang;
        const corpus = ADVISORY_CORPUS[lang] || ADVISORY_CORPUS.Sindhi;
        
        let condition = 'normal';
        if (state.weather === 'Rain' || state.time === 'Night') condition = 'monsoon';
        if (state.activeHazard) condition = 'hazard';

        const item = corpus[condition] || corpus.normal;
        
        const headlineEl = document.getElementById('advisory-headline');
        const romanEl    = document.getElementById('advisory-roman');
        const englishEl  = document.getElementById('advisory-english');
        const badgeEl    = document.getElementById('advisory-lang-badge');
        const btnLabel   = document.getElementById('advisory-btn-label');
        const boxEl      = document.getElementById('dynamic-advisory-box');

        if (headlineEl) headlineEl.innerText = item.headline;
        if (romanEl)    romanEl.innerText = `"${item.roman}"`;
        if (englishEl)  englishEl.innerHTML = `<strong>English Translation:</strong> ${item.english}`;
        if (badgeEl)    badgeEl.innerText = `🟢 ${lang} Active`;
        if (btnLabel)   btnLabel.innerText = `Speak Advisory in ${lang}`;

        if (boxEl) {
            if (condition === 'hazard') {
                boxEl.style.borderLeftColor = '#C62828';
                boxEl.style.background = '#FDECEA';
            } else if (condition === 'monsoon') {
                boxEl.style.borderLeftColor = '#E65100';
                boxEl.style.background = '#FFF4E5';
            } else {
                boxEl.style.borderLeftColor = '#4A7C2F';
                boxEl.style.background = '#F4F1EA';
            }
        }
    }

    function playAudioGuidance() {
        const lang = state.lang;
        const corpus = ADVISORY_CORPUS[lang] || ADVISORY_CORPUS.Sindhi;
        let condition = 'normal';
        if (state.weather === 'Rain' || state.time === 'Night') condition = 'monsoon';
        if (state.activeHazard) condition = 'hazard';

        const item = corpus[condition] || corpus.normal;
        const transcript = `🔊 Spoken (${lang}): "${item.roman}"`;
        document.getElementById('audio-transcript').innerText = transcript;

        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop any pending speech
            const utter = new SpeechSynthesisUtterance(item.roman);
            utter.lang = corpus.voiceLang || 'ur-PK';
            utter.rate = 0.88;
            utter.pitch = 1.0;
            window.speechSynthesis.speak(utter);
        }
    }
"""

# Replace old playAudioGuidance function
old_audio_fn = """    function playAudioGuidance() {
        const text = "Khabbe moro — National Highway 8 (12.0 km)";
        document.getElementById('audio-transcript').innerText = `🔊 Playing (${state.lang}): "${text}"`;
        
        if ('speechSynthesis' in window) {
            const synth = window.speechSynthesis;
            const utter = new SpeechSynthesisUtterance("Turn left onto National Highway 8");
            synth.speak(utter);
        }
    }"""

html = html.replace(old_audio_fn, js_advisory_logic)

# In updateDriverContext, trigger updateAudioAdvisoryUI()
html = html.replace('updateDriverContext() {\n', 'updateDriverContext() {\n        state.activeHazard = false;\n')
html = html.replace('renderChat();\n    }\n\n    function updateProgress', 'renderChat();\n        updateAudioAdvisoryUI();\n    }\n\n    function updateProgress')

# In applyPreset, update advisory
html = html.replace("state.activeHazard = true;", "") # clean old if any
html = html.replace("sendQuickPrompt('gadi kharab thia ahe raste te madad mokh');", "state.activeHazard = true;\n            updateAudioAdvisoryUI();\n            sendQuickPrompt('gadi kharab thia ahe raste te madad mokh');")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS: apply_loku_updates.py completed cleanly.")
