"""
Agri-Logistics IDAS — Intelligent Driver Assistance System
Production-Grade Research Prototype — Phase 3 (Context-Aware Safety)

Author      : Lokesh Kumar
Student ID  : 2k22-SE-42
Email       : 2K22-SE-42@student.sau.edu.pk
Institution : Sindh Agriculture University, Tandojam

Research Paper Title:
    "Bridging the Digital Literacy Gap in Rural Agri-Logistics:
     A Trilingual, Context-Aware Intelligent Driver Assistance System
     for the Sindh Agricultural Supply Chain"

Submitted to: Sindh Agriculture University, Tandojam
"""

import io
import inspect
import streamlit as st
import streamlit_folium as sf

# ── MONKEY-PATCH st_folium FOR UNIQUE DETERMINISTIC KEYS ──────────
_original_st_folium = sf.st_folium

def patched_st_folium(fig, *args, **kwargs):
    if "key" not in kwargs or kwargs["key"] is None:
        # Trace back to find caller function name (e.g. plot_route_on_map)
        frame = inspect.currentframe().f_back
        func_name = frame.f_code.co_name if frame else "unknown"
        height = kwargs.get("height", "default")
        # Generate a unique, layout-deterministic key
        kwargs["key"] = f"auto_map_{func_name}_{height}"
    return _original_st_folium(fig, *args, **kwargs)

sf.st_folium = patched_st_folium

import streamlit.components.v1 as components
from routing import (
    get_osrm_route,
    plot_route_on_map,
    plot_fallback_map,
    get_route_map_html,
    get_fallback_map_html,
)
from voice_advisory import generate_voice_advisory

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: MOCK NLP TRANSLATOR
# ═══════════════════════════════════════════════════════════════════

# ── Known hazard phrases from driver → Corporate English ────────────
# Supports all three regional dialects: Sindhi, Urdu, Dhatki
HAZARD_PHRASES: dict = {
    # Bridge hazards
    "pul budi wai ahe":      "⚠️ The bridge is flooded.",
    "pul doob gaya hai":     "⚠️ The bridge is flooded.",
    "pul buday gayo hai":     "⚠️ The bridge is flooded.",
    "pul band ahey":          "⚠️ The bridge is closed — route blocked.",
    "pul band hai":          "⚠️ The bridge is closed — route blocked.",
    # Road blockages
    "sadak bund ahe":        "🚧 The road is blocked ahead.",
    "sadak band hai":        "🚧 The road is blocked ahead.",
    "rasto band hai":         "🚧 The road is blocked ahead.",
    # Weather
    "tez barish ahe":        "🌧️ Driver reports heavy rainfall on route.",
    "tez baarish hai":       "🌧️ Driver reports heavy rainfall on route.",
    "barsat tezz hai":     "🌧️ Driver reports heavy rainfall on route.",
    # Vehicle breakdown
    "gaadi kharab thi wahi ahay":     "🔧 Vehicle breakdown — driver requires assistance.",
    "gaadi kharab hui hai":  "🔧 Vehicle breakdown — driver requires assistance.",
    "gaadi kharab thi hai":     "🔧 Vehicle breakdown — driver requires assistance.",
    "gadi kharab ahe":       "🔧 Vehicle breakdown — driver requires assistance.",
    # Cargo spoilage
    "tamatar kharab thi wya":   "🍅 Produce spoilage risk — fragile cargo compromised.",
    "tamatar bigad rahe":    "🍅 Produce spoilage risk — fragile cargo compromised.",
    "tamata kharab thai ae":   "🍅 Produce spoilage risk — fragile cargo compromised.",
    # Traffic
    "rasto jam ahe":        "🚦 Traffic congestion reported by driver.",
    "trafik jam hai":        "🚦 Traffic congestion reported by driver.",
    "rasto jam hai":       "🚦 Traffic congestion reported by driver.",
    # Livestock / road hazard
    "janwar raste te aahay": "🐄 Livestock on the road — caution advised.",
    "janwar sadak par hai":  "🐄 Livestock on the road — caution advised.",
    "janwar raste te hai":  "🐄 Livestock on the road — caution advised.",
}

# ── Corporate English commands → Native dialect translations ────────
CORPORATE_COMMANDS: dict = {
    "delay tomato pickup by 2 hours": {
        "Sindhi":  "Tamatar khahrn me 2 kalak ji dair ahe",
        "Urdu":    "Tamatar uthane mein 2 ghante ki der hai",
        "Dhatki":  "Tamata kaharn mein 2 kalak ri dair hai",
    },
    "delay pickup": {
        "Sindhi":  "Kharn mein dair ahey",
        "Urdu":    "Uthane mein der hai",
        "Dhatki":  "kahrarn mein dair hai",
    },
    "reroute due to weather": {
        "Sindhi":  "Mosam kharab ahey, nayo rasto vanjo",
        "Urdu":    "Mausam kharab hai, naya rasta lo",
        "Dhatki":  "mosam kharab hai, bijo rasto jao",
    },
    "stop and wait": {
        "Sindhi":  "Rokio ۽ Intezaar kayo",
        "Urdu":    "Ruko aur intezaar karein",
        "Dhatki":  "roko ayi sabar karo",
    },
    "proceed to delivery": {
        "Sindhi":  "Delivery waari wanjio",
        "Urdu":    "Delivery ki taraf chalein",
        "Dhatki":  "Delivery ri taraf jao",
    },
    "welcome to idas network": {
        "Sindhi":  "IDAS Network mein khush aayo",
        "Urdu":    "IDAS Network mein khush aamdeed",
        "Dhatki":  "IDAS Network mein khushi aao avi",
    },
    "check your cargo": {
        "Sindhi":  "Panjo maal check karo",
        "Urdu":    "Apna maal check karein",
        "Dhatki":  "apro maal joo",
    },
    "estimated arrival in 2 hours": {
        "Sindhi":  "2 kalak mein pohchi windas",
        "Urdu":    "2 ghante mein pahunchne ki umeed hai",
        "Dhatki":  "2 kalak mein ppohche jais ro",
    },
    "take the alternate route": {
        "Sindhi":  "Biyo rasto vanjo",
        "Urdu":    "Doosra rasta lo",
        "Dhatki":  "Bijay raste jao",
    },
}


def mock_translate(text: str, target_lang: str) -> str:
    """
    Bidirectional NLP mock translator for the Agri-Logistics IDAS.

    Modes:
      Driver → Corporate  : target_lang = "English"
          Detects known regional hazard phrases (Sindhi / Urdu / Dhatki)
          and returns the English translation with a status emoji.

      Corporate → Driver  : target_lang in {"Sindhi", "Urdu", "Dhatki"}
          Detects known English corporate commands and returns the
          translation in the driver's selected regional dialect.

    Fallback:
          Returns a bracketed placeholder for unrecognised phrases.
    """
    t = text.lower().strip()

    # Driver → English (hazard detection)
    if target_lang == "English":
        for phrase, translation in HAZARD_PHRASES.items():
            if phrase in t:
                return translation
        return f"[Translated to English]: {text}"

    # English → Native dialect (corporate command detection)
    for phrase, translations in CORPORATE_COMMANDS.items():
        if phrase in t:
            return translations.get(target_lang, text)

    # Generic fallback
    return f"[Translated to {target_lang}]: {text}"


def is_hazard_message(text: str) -> bool:
    """
    Return True if `text` contains a known hazard phrase.
    Used by the Corporate Dashboard to display a high-priority alert banner.
    """
    t = text.lower().strip()
    return any(phrase in t for phrase in HAZARD_PHRASES)


# ─────────────────────────────────────────────────────────────────
# CHAT RENDERER
# Each message is rendered as a single, small st.markdown() call.
# This approach is compatible with every Streamlit version (1.0+)
# and works correctly inside any column or container.
# ─────────────────────────────────────────────────────────────────

def _render_chat(
    messages: list,
    view: str = "corporate",
    target_lang: str = "Sindhi",
    height: int = 270,
) -> None:
    """
    Render chat messages as custom styled HTML bubbles.

    Each message is rendered as a single small st.markdown() call
    with unsafe_allow_html=True.  Individual short HTML snippets are
    always rendered correctly by Streamlit — only large concatenated
    HTML blobs risk being emitted as escaped text.

    The CSS classes (.chat-row, .bubble-driver, etc.) are defined in
    the global <style> block injected at app startup, so they apply
    automatically to every snippet.

    Parameters
    ----------
    messages    : st.session_state.chat_messages list.
    view        : "corporate" — show English text.
                  "driver"    — translate corporate messages to target_lang.
    target_lang : Driver's selected language (only used when view=="driver").
    height      : Unused — kept for API compatibility.
    """
    for msg in messages:
        is_driver = (msg["role"] == "driver")
        row_cls  = "driver" if is_driver else "corporate"
        bbl_cls  = "bubble-driver" if is_driver else "bubble-corporate"
        avatar   = "🚚" if is_driver else "🏢"
        av_cls   = "avatar-drv" if is_driver else "avatar-corp"
        meta_cls = "meta-right" if is_driver else "meta-left"

        if view == "corporate":
            display_text = msg["english"]
            badge = (
                f"🌐 {msg.get('source_lang', '?')} → EN"
                if is_driver
                else "🏢 Corporate"
            )
        else:
            if is_driver:
                display_text = msg["original"]
                badge = f"You ({target_lang})"
            else:
                display_text = mock_translate(
                    msg["english"].lower(), target_lang
                )
                badge = f"🏢 → {target_lang}"

        st.markdown(
            f'<div class="chat-row {row_cls}">'
            f'<div class="chat-avatar {av_cls}">{avatar}</div>'
            f'<div class="chat-bubble-wrap">'
            f'<div class="chat-bubble {bbl_cls}">{display_text}</div>'
            f'<div class="chat-meta {meta_cls}">{badge}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════
# SECTION 2: DYNAMIC CONTEXT-AWARE SAFETY DATA
# ═══════════════════════════════════════════════════════════════════

# Safety text per alert level, per language.
# Structure: {level_key: {lang: (title, body_message)}}
# The "English" entry is always present as the fallback.
SAFETY_TEXT: dict = {

    # ── Tier 4: EXTREME — Night + Rain + Fragile (all three) ──────
    "extreme": {
        "English": (
            "⛔  EXTREME RISK: Night + Rain + Fragile Cargo",
            "All three critical hazard factors are active simultaneously. "
            "Reduce speed by 50%, activate hazard lights immediately, move away "
            "from road shoulders, and consider pulling over safely until the rain "
            "subsides. Do not attempt overtaking under any circumstances.",
        ),
        "Sindhi": (
            "⛔  INTEHAIYI KHATRO: Raat + Barish + Nazuk Maal",
            "Teno khatarnak halat hik waqt gad thia aahin. "
            "Raftar 50% ghat karo. Hazard lights hinner chalao. "
            "Sadak ji kirri chhad. Barish rukay taan gaadi rokyo. "
            "Keh khe overtake na karo.",
        ),
        "Urdu": (
            "⛔  انتہائی خطرہ: رات + بارش + نازک مال",
            "Teen khatarnak halaat ek waqt par hain. "
            "Raftar 50% fauran kam karein. Hazard lights on karein. "
            "Sadak ke kinare se hat jayein. Baarish rukne tak gaadi rokein. "
            "Kisi bhi soorat mein overtake na karein.",
        ),
        "Dhatki": (
            "⛔  BAHUT BARO KHATRO: Raat + Meh + Nazuk Bojh",
            "Teen khatarnak haalat bhera hai. "
            "Chaal 50% heran ghat karo. Hazard batti hera jalao. "
            "Sadak ri jhalar chhad. Meh rukay takaar gadi rokyo. "
            "Keh kha bhi agya na jao.",
        ),
    },

    # ── Tier 3: CRITICAL — Rain + Fragile (without night) ─────────
    "critical": {
        "English": (
            "🛑  CRITICAL: Wet Roads + Fragile Cargo",
            "Roads are slippery and cargo is highly perishable. "
            "Reduce speed by 30%, increase following distance to 6 seconds, "
            "and avoid sudden braking to prevent crop bruising and cargo loss.",
        ),
        "Sindhi": (
            "🛑  KHATARNAK: Giili Sadak + Nazuk Maal",
            "Sadak chikani ahe ۽ maal nazuk ahe. "
            "Raftar 30% ghat karo. Aagey waari gaadi thon 6 second door raho. "
            "Achanak brake na kayo — tamatar kharab thia ۽ nuksaan thindo.",
        ),
        "Urdu": (
            "🛑  خطرناک: گیلی سڑک + نازک مال",
            "Sadak phisal-dari hai aur maal nazuk hai. "
            "Raftar 30% kam karein. Aagey wali gaadi se 6 second dur rahein. "
            "Achanak brake na dein — tamatar kharab aur nuksaan hoga.",
        ),
        "Dhatki": (
            "🛑  KHATARNAK: Gehli Sadak + Nazuk Bojh",
            "Raste main pani hai ayi bojh nazuk ahe. "
            "Chaal 30% ghat karo. Agay ri gadi kha 6 second dur raho. "
            "Ochto roko na karo — tamatar kharab ayi nuksaan the jasay.",
        ),
    },

    # ── Tier 2: WARNING (Fragile only) ────────────────────────────
    "warning_fragile": {
        "English": (
            "🍅  CAUTION: Delicate Payload Detected",
            "Perishable produce on board. Brake gently when approaching turns, "
            "avoid sudden acceleration, and take speed bumps at very low speed "
            "to prevent crop bruising and post-harvest losses.",
        ),
        "Sindhi": (
            "🍅  KHABARDAR: Nazuk Maal Gadi Mein Aahay",
            "Tamatar ۽ nazuk maal gadi mein aahay. "
            "Mod waray ahista brake kayo. Achanak tez na thio. "
            "Speed bump slow karke langho — tamatar zaya na thia.",
        ),
        "Urdu": (
            "🍅  خبردار: نازک مال سوار ہے",
            "Tamatar aur nazuk maal gadi mein hai. "
            "Mod par dheere brake lagayein. Achanak tez mat karein. "
            "Speed bump dheerey parein — tamatar kharab na hon.",
        ),
        "Dhatki": (
            "🍅  KHABARDAR: Nazuk Bojh Gadi Mein Aahay",
            "Tamatar ane nazuk bojh gadi mein hai. "
            "morr te ahista gadi halaya. Achanak tez na karya. "
            "Speed bump te ahista thiya — tamatar zaya na thia.",
        ),
    },

    # ── Tier 2: WARNING (Night + Rain, no fragile) ────────────────
    "warning_night_rain": {
        "English": (
            "🌧️  SEVERE: Night + Rain — Very Low Visibility",
            "Nighttime and heavy rain detected on your route. Turn on fog lights "
            "immediately, avoid overtaking on single-lane roads, and watch for "
            "unlit agricultural vehicles and stray livestock.",
        ),
        "Sindhi": (
            "🌧️  SANJIDA: Raat + Barish — Ghat Dikhai",
            "Raat ahe ۽ barish payi ahey. "
            "Fog lights hiyar halaoo. Hik lane wari sadak te overtake na karo. "
            "Bina batti gadi ۽ janwaron thon khabardar raho.",
        ),
        "Urdu": (
            "🌧️  سنگین: رات + بارش — نظر بہت کم",
            "Raat hai aur baarish ho rahi hai. "
            "Fog lights fauran on karein. Single-lane sadak par overtake na karein. "
            "Bina batti gariyon aur jaanwaaron se khabardar rahein.",
        ),
        "Dhatki": (
            "🌧️  GAMBHIR: Raat + Meh — Thori Dikh",
            "Raat ahe ane meh aavti ahe. "
            "Fog batti hera jalao. Hik lane wari raah te aagya na jao. "
            "Bina batti gadi ane janwaron ro khayal rakho.",
        ),
    },

    # ── Tier 2: WARNING (Night only) ──────────────────────────────
    "warning_night": {
        "English": (
            "🌙  NIGHT ETIQUETTE ACTIVE",
            "Sun has set. Activate headlights, beware of stray livestock "
            "on rural roads, and dim high-beams for oncoming traffic.",
        ),
        "Sindhi": (
            "🌙  RAAT JO USOOL LAAGO",
            "Sooraj lahyo ahe. Headlights jalao. "
            "goth ji sadak te janwaron thon cheti raho. "
            "Samhni aaindi gaadi waste lights dim karo.",
        ),
        "Urdu": (
            "🌙  رات کے اصول نافذ",
            "Sooraj ghurub ho gaya hai. Headlights on karein. "
            "Gaon ki sadakon par jaanwaaron se hoshiyar rahein. "
            "Samne aane wali gaadi ke liye lights dim karein.",
        ),
        "Dhatki": (
            "🌙  RAAT RO DHANG LAAGO",
            "Sooraj hetho the pyo. Headlights halao. "
            "goth ri raah waaro janwaron ro dhiyan rakho. "
            "Samu aati gadi waste lights dim karo.",
        ),
    },

    # ── Tier 2: WARNING (Rain only) ───────────────────────────────
    "warning_rain": {
        "English": (
            "🌦️  WET CONDITIONS AHEAD",
            "Light to moderate rain detected along your route. "
            "Braking distance is significantly increased on wet roads. "
            "Drive carefully and avoid flooded or waterlogged sections.",
        ),
        "Sindhi": (
            "🌦️  GIILI SADAK AAGEY",
            "Rasto te barish payi ahe. "
            "Giili sadak te brake distance vaddhi viyi ahe. "
            "Ahista halo ۽ paani bharil sadak thon paria raho.",
        ),
        "Urdu": (
            "🌦️  آگے گیلی سڑک",
            "Raaste par baarish ho rahi hai. "
            "Geeli sadak par braking distance barh gayi hai. "
            "Aahista chalein aur paani bhari sadak se parhez karein.",
        ),
        "Dhatki": (
            "🌦️  AAGEY GEHLI RAAH",
            "Raah te meh barsat thi hai. "
            "Gilay raste te break thoro pehri harya. "
            "Ahista jaya ane paani bharil raste kha paray rahya.",
        ),
    },

    # ── Tier 1: STANDARD (all clear) ──────────────────────────────
    "standard": {
        "English": (
            "ℹ️  Standard Driving Parameters",
            "Route conditions are clear. Maintain standard driving etiquette, "
            "observe local speed limits, and stay hydrated on long hauls.",
        ),
        "Sindhi": (
            "ℹ️  MAMULI HALAT",
            "Rasto saaf ahe. "
            "Mamuli driving karo ۽ local speed limit manno. "
            "Lamba safar mein paani pinda raho.",
        ),
        "Urdu": (
            "ℹ️  معمول کے حالات",
            "Rasta saaf hai. "
            "Mamuli andaz mein chalein aur local speed limit ka khayal rakhein. "
            "Lambe safar mein paani peete rahein.",
        ),
        "Dhatki": (
            "ℹ️  SADHAARAN HALAT",
            "Raah saaf hai. "
            "Aaram sa halo ayi speed limit ghat rakho. "
            "waday safar mein paani pitaa raho.",
        ),
    },
}


def get_safety_context(
    cargo_type: str,
    time_of_day: str,
    weather: str,
    language: str,
) -> tuple:
    """
    Evaluate context parameters and return the appropriate safety tier.

    Priority hierarchy (highest to lowest):
        extreme        — Night + Rain + Fragile (all three)
        critical       — Rain + Fragile
        warning_fragile— Fragile only
        warning_night_rain — Night + Rain (no fragile)
        warning_night  — Night only
        warning_rain   — Rain only
        standard       — No hazards detected

    Returns
    -------
    tuple: (css_class, title, message, english_title)
        css_class     : CSS class name for the alert div ("extreme",
                        "critical", "warning", "standard")
        title         : Localised alert title string
        message       : Localised alert body string
        english_title : English title (always English for corporate log)
    """
    is_fragile = (cargo_type == "Fragile / Tomatoes")
    is_night   = (time_of_day == "Night")
    is_rain    = (weather == "Rain")

    # Determine alert tier
    if is_fragile and is_night and is_rain:
        level     = "extreme"
        css_class = "extreme"
    elif is_fragile and is_rain:
        level     = "critical"
        css_class = "critical"
    elif is_fragile:
        level     = "warning_fragile"
        css_class = "warning"
    elif is_night and is_rain:
        level     = "warning_night_rain"
        css_class = "warning"
    elif is_night:
        level     = "warning_night"
        css_class = "warning"
    elif is_rain:
        level     = "warning_rain"
        css_class = "warning"
    else:
        level     = "standard"
        css_class = "standard"

    # Retrieve localised text; fall back to English if language not found
    texts    = SAFETY_TEXT[level]
    lang_key = language if language in texts else "English"
    title, message = texts[lang_key]

    # Always retrieve the English title for the corporate dashboard log
    eng_title, _ = texts["English"]

    return css_class, title, message, eng_title


# ═══════════════════════════════════════════════════════════════════
# SECTION 3: STREAMLIT PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Agri-Logistics IDAS · SAU Tandojam",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════
# SECTION 4: CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
    /* ── Google Font: Inter ───────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App background ──────────────────────────────────────── */
    .stApp {
        background-color: #F5F2EC;
    }

    /* ── Hide Streamlit menu & footer ───────────────────────── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    /* ── Sidebar background ──────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111A06 0%, #1E2E0A 60%, #2A3F10 100%);
        border-right: 1px solid #3A5215;
    }
    [data-testid="stSidebar"] * {
        color: #D0DEB8 !important;
    }

    /* ── Academic Author Card ───────────────────────────────── */
    .academic-card {
        background: linear-gradient(160deg, #1A2409 0%, #243310 100%);
        border: 1px solid #5A4A1A;
        border-left: 4px solid #D4AF37;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
    }
    .ac-badge {
        background: #D4AF37;
        color: #1A1000;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
    }
    .ac-name {
        color: #F5E6A3 !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0 0 2px 0;
        line-height: 1.2;
    }
    .ac-id {
        color: #D4AF37 !important;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0 0 12px 0;
    }
    .ac-divider {
        border: none;
        border-top: 1px solid #3A4F1A;
        margin: 10px 0;
    }
    .ac-row {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 7px;
    }
    .ac-icon {
        font-size: 0.8rem;
        min-width: 16px;
        margin-top: 1px;
    }
    .ac-text {
        color: #B8CDA0 !important;
        font-size: 0.76rem;
        line-height: 1.45;
    }
    .ac-uni {
        color: #C8D8A0 !important;
        font-size: 0.78rem;
        font-weight: 600;
        line-height: 1.4;
    }

    /* ── Sidebar section label ──────────────────────────────── */
    .sidebar-section-label {
        color: #6B8A45 !important;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 18px 0 8px 0;
    }

    /* ── App header banner ──────────────────────────────────── */
    .app-header {
        background: linear-gradient(135deg, #1E3A0F 0%, #2D5016 50%, #3D6B22 100%);
        border-radius: 14px;
        padding: 22px 32px;
        margin-bottom: 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(45, 80, 22, 0.25);
    }
    .app-header h1 {
        color: #FFFFFF;
        font-size: 1.65rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .app-header p {
        color: #C5DFA0;
        font-size: 0.82rem;
        margin: 5px 0 0 0;
    }
    .header-right {
        text-align: right;
    }
    .header-badge {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        color: #FFFFFF;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.8px;
        display: inline-block;
        margin-bottom: 4px;
    }
    .header-author {
        color: #D4AF37;
        font-size: 0.72rem;
        font-weight: 600;
        margin-top: 4px;
    }

    /* ── Tab bar ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #EAE6DE;
        border-radius: 12px;
        padding: 6px;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #5C6B4A;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 10px 26px;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #2D5016 !important;
        box-shadow: 0 2px 10px rgba(45, 80, 22, 0.14);
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab-panel"]  { padding-top: 22px; }

    /* ── KPI metric cards ───────────────────────────────────── */
    .metric-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 20px 22px;
        border-left: 5px solid #4A7C2F;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.11);
    }
    .metric-card h3 {
        color: #8A9E78;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 8px 0;
    }
    .metric-card .metric-value {
        color: #1E3A0F;
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1;
        margin: 0 0 6px 0;
    }
    .metric-card .metric-delta {
        font-size: 0.78rem;
        font-weight: 500;
    }
    .metric-card .metric-delta.positive { color: #2D6A1A; }
    .metric-card .metric-delta.neutral  { color: #7A6A2F; }
    .metric-card .metric-delta.negative { color: #8A0000; }

    /* ── Section cards ──────────────────────────────────────── */
    .section-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        margin-bottom: 18px;
    }
    .section-card h4 {
        color: #2D5016;
        font-size: 0.92rem;
        font-weight: 700;
        margin: 0 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid #EAE6DE;
    }

    /* ── Route info badges ──────────────────────────────────── */
    .route-info-row {
        display: flex;
        gap: 12px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .route-badge {
        background: #F0EDE6;
        border: 1px solid #D8D0C0;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #2D5016;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* ── Status pills ───────────────────────────────────────── */
    .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .pill-green  { background: #D6EFC4; color: #1E5C12; }
    .pill-orange { background: #FDE8C8; color: #7A4000; }
    .pill-red    { background: #FDD5D5; color: #7A0000; }
    .pill-blue   { background: #D0E8FF; color: #003A7A; }

    /* ── Driver panel ───────────────────────────────────────── */
    .driver-panel {
        background: linear-gradient(160deg, #1E3A0F 0%, #2D5016 100%);
        border-radius: 16px;
        padding: 26px 28px;
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(30, 58, 15, 0.3);
    }
    .driver-panel h2 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0 0 4px 0;
    }
    .driver-panel .sub {
        color: #A8C87E;
        font-size: 0.8rem;
        margin: 0;
    }
    .driver-info-row {
        display: flex;
        gap: 28px;
        margin-top: 18px;
        flex-wrap: wrap;
    }
    .driver-info-item label {
        color: #7A9E55;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: block;
        margin-bottom: 3px;
    }
    .driver-info-item span {
        color: #FFFFFF;
        font-size: 0.9rem;
        font-weight: 600;
    }

    /* ── Cargo badges ───────────────────────────────────────── */
    .cargo-standard {
        background: #D6EFC4;
        color: #1E5C12;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
    }
    .cargo-fragile {
        background: #FDE8C8;
        color: #7A4000;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
    }

    /* ── Divider ────────────────────────────────────────────── */
    hr.agri-hr {
        border: none;
        border-top: 1px solid #DDD8CD;
        margin: 18px 0;
    }

    /* ── Widget label overrides ─────────────────────────────── */
    label[data-testid="stWidgetLabel"] > div > p {
        font-weight: 600 !important;
        color: #2D5016 !important;
        font-size: 0.82rem !important;
    }

    /* ── Safety alert panels ────────────────────────────────── */
    .safety-alert {
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 18px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        border-left: 5px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }
    .safety-alert.standard {
        background: #E8F4FD;
        border-color: #2196F3;
        color: #0C4375;
    }
    .safety-alert.warning {
        background: #FFF4E5;
        border-color: #FF9800;
        color: #6B3800;
    }
    .safety-alert.critical {
        background: #FDECEA;
        border-color: #F44336;
        color: #6A1911;
        animation: pulse-glow-red 2s infinite;
    }
    .safety-alert.extreme {
        background: #1A0505;
        border-color: #FF0000;
        color: #FFD0CC;
        animation: pulse-glow-extreme 1s infinite;
    }
    .safety-icon {
        font-size: 1.9rem;
        line-height: 1;
        flex-shrink: 0;
    }
    .safety-text h5 {
        margin: 0 0 6px 0;
        font-size: 0.92rem;
        font-weight: 800;
    }
    .safety-text p {
        margin: 0;
        font-size: 0.83rem;
        line-height: 1.6;
    }
    .safety-alert.extreme .safety-text h5 {
        color: #FF8080;
    }
    .safety-alert.extreme .safety-text p {
        color: #FFB0A8;
    }

    /* ── Pulse animations ───────────────────────────────────── */
    @keyframes pulse-glow-red {
        0%   { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4); }
        70%  { box-shadow: 0 0 0 8px rgba(244, 67, 54, 0); }
        100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
    }
    @keyframes pulse-glow-extreme {
        0%   { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        50%  { box-shadow: 0 0 20px 6px rgba(255, 0, 0, 0.4); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.0); }
    }

    /* ── Hazard alert banner (corporate tab) ────────────────── */
    .hazard-banner {
        background: linear-gradient(135deg, #C62828, #E53935);
        color: #FFFFFF;
        border-radius: 10px;
        padding: 12px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 12px;
        animation: pulse-glow-extreme 1.5s infinite;
        box-shadow: 0 2px 12px rgba(198, 40, 40, 0.4);
    }
    .hazard-banner-icon { font-size: 1.4rem; }
    .hazard-banner-text { line-height: 1.4; }
    .hazard-banner-text small {
        display: block;
        font-weight: 400;
        font-size: 0.75rem;
        opacity: 0.85;
        margin-top: 2px;
    }

    /* ── Custom chat bubbles ────────────────────────────────── */
    .chat-scroll-box {
        height: 260px;
        overflow-y: auto;
        padding: 14px 10px;
        background: #FAFAF8;
        border-radius: 10px;
        border: 1px solid #EAE6DE;
        margin-bottom: 10px;
    }
    .chat-row {
        display: flex;
        margin-bottom: 12px;
        align-items: flex-end;
        gap: 6px;
    }
    .chat-row.driver   { flex-direction: row-reverse; }
    .chat-row.corporate{ flex-direction: row; }
    .chat-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
    .avatar-corp {
        background: #EAE6DE;
    }
    .avatar-drv {
        background: linear-gradient(135deg, #2D5016, #4A7C2F);
    }
    .chat-bubble-wrap { max-width: 75%; }
    .chat-bubble {
        padding: 9px 13px;
        border-radius: 14px;
        font-size: 0.83rem;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .bubble-corporate {
        background: #EDEBE4;
        color: #2D3A1F;
        border-bottom-left-radius: 4px;
    }
    .bubble-driver {
        background: linear-gradient(135deg, #2D5016, #4A7C2F);
        color: #FFFFFF;
        border-bottom-right-radius: 4px;
    }
    .chat-meta {
        font-size: 0.63rem;
        color: #A09880;
        margin-top: 3px;
        padding: 0 3px;
    }
    .meta-right { text-align: right; }
    .meta-left  { text-align: left; }

    /* ── Navigation placeholder ─────────────────────────────── */
    .nav-placeholder {
        background: #F0EDE6;
        border: 2px dashed #C8C0A8;
        border-radius: 10px;
        height: 230px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 8px;
        color: #9A9280;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 6px;
    }

    /* ── Telemetry card ─────────────────────────────────────── */
    .tele-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #F0EDE6;
    }
    .tele-label {
        color: #8A9E78;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .tele-value {
        color: #1E3A0F;
        font-size: 0.88rem;
        font-weight: 700;
    }
    .tele-pending {
        color: #B0A890;
        font-size: 0.75rem;
        font-style: italic;
    }

    /* ── IEEE footer ────────────────────────────────────────── */
    .ieee-footer {
        background: linear-gradient(135deg, #111A06 0%, #1E2E0A 100%);
        border-top: 1px solid #3A5215;
        border-radius: 14px;
        padding: 20px 28px;
        margin-top: 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        flex-wrap: wrap;
    }
    .ieee-footer .footer-left {
        flex: 1;
    }
    .ieee-footer .footer-title {
        color: #D4AF37;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .ieee-footer .footer-citation {
        color: #A0B880;
        font-size: 0.72rem;
        line-height: 1.7;
    }
    .ieee-footer .footer-citation em {
        color: #C8D8A0;
        font-style: normal;
        font-weight: 600;
    }
    .ieee-footer .footer-right {
        text-align: right;
        color: #6B8A45;
        font-size: 0.7rem;
        line-height: 1.7;
    }
    .footer-dot {
        display: inline-block;
        width: 5px;
        height: 5px;
        background: #D4AF37;
        border-radius: 50%;
        margin: 0 6px;
        vertical-align: middle;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════
# SECTION 5: SESSION STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

DEFAULTS: dict = {
    "driver_language":   "Sindhi",
    "cargo_type":        "Standard",
    "time_of_day":       "Day",
    "weather":           "Clear",
    "driver_name":       "Muhammad Saleem",
    "driver_id":         "DRV-0042",
    "vehicle_id":        "TRK-119",
    "current_route":     "Mithi → Hyderabad",
    "hazard_active":     False,
    "last_hazard_msg":   "",
    "route_instructions": [],
    "route_distance_km": None,
    "route_duration_min": None,
    "route_geometry":     None,
    "route_loaded":       False,
    "route_fallback":     False,
    "chat_messages": [
        {
            "role":        "corporate",
            "original":    "Welcome to IDAS Network.",
            "english":     "Welcome to IDAS Network.",
            "source_lang": "English",
        }
    ],
}

for _key, _val in DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val

# Constants for dropdowns
LANGUAGES    = ["Sindhi", "Urdu", "Dhatki"]
CARGO_TYPES  = ["Standard", "Fragile / Tomatoes"]
TIME_OPTS    = ["Day", "Night"]
WEATHER_OPTS = ["Clear", "Rain"]

CARGO_LABELS: dict = {
    "Standard":            ("cargo-standard", "📦 Standard"),
    "Fragile / Tomatoes":  ("cargo-fragile",  "🍅 Fragile / Tomatoes"),
}
LANG_FLAG: dict = {"Sindhi": "🟢", "Urdu": "🔵", "Dhatki": "🟡"}


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: ACADEMIC AUTHOR SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        """
        <div class="academic-card">
            <div class="ac-badge">🎓 Research Author</div>
            <p class="ac-name">Lokesh Kumar</p>
            <p class="ac-id">Student ID: 2k22-SE-42</p>
            <hr class="ac-divider">
            <div class="ac-row">
                <span class="ac-icon">📧</span>
                <span class="ac-text">2K22-SE-42@student.sau.edu.pk</span>
            </div>
            <div class="ac-row">
                <span class="ac-icon">🏛️</span>
                <span class="ac-uni">Sindh Agriculture University<br>Tandojam</span>
            </div>
            <div class="ac-row">
                <span class="ac-icon">📄</span>
                <span class="ac-text">Dept. of Software Engineering</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="sidebar-section-label">📋 Research Context</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="color:#8AB065; font-size:0.73rem; line-height:1.7; 
                    background:#1A2409; border-radius:10px; padding:14px;">
            <strong style="color:#C8D8A0;">Title:</strong><br>
            <em style="color:#A8C880;">Bridging the Digital Literacy Gap in 
            Rural Agri-Logistics Using a Trilingual, Context-Aware IDAS</em>
            <br><br>
            <strong style="color:#C8D8A0;">Objective:</strong><br>
            <span style="color:#8AB065;">Zero-literacy-barrier access to route 
            safety for Sindhi, Urdu, and Dhatki-speaking drivers.</span>
            <br><br>
            <strong style="color:#C8D8A0;">Prototype Phase:</strong>
            <span style="color:#D4AF37; font-weight:700;"> Phase 3 ✓</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="sidebar-section-label">🚚 Active Asset</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="color:#8AB065; font-size:0.73rem; line-height:1.9;
                    background:#1A2409; border-radius:10px; padding:14px;">
            <strong style="color:#C8D8A0;">Driver:</strong>
            <span style="color:#FFFFFF;">  {st.session_state["driver_name"]}</span><br>
            <strong style="color:#C8D8A0;">ID:</strong>
            <span style="color:#D4AF37;">  {st.session_state["driver_id"]}</span><br>
            <strong style="color:#C8D8A0;">Vehicle:</strong>
            <span style="color:#FFFFFF;">  {st.session_state["vehicle_id"]}</span><br>
            <strong style="color:#C8D8A0;">Route:</strong>
            <span style="color:#A8C880;">  {st.session_state["current_route"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="sidebar-section-label">ℹ️ System Status</p>',
        unsafe_allow_html=True,
    )
    hazard_status = (
        "🔴 HAZARD ACTIVE"
        if st.session_state.get("hazard_active", False)
        else "🟢 All Clear"
    )
    st.markdown(
        f"""
        <div style="font-size:0.73rem; line-height:1.9;
                    background:#1A2409; border-radius:10px; padding:14px;">
            <strong style="color:#C8D8A0;">OSRM Routing:</strong>
            <span style="color:#A8C880;"> Live</span><br>
            <strong style="color:#C8D8A0;">NLP Layer:</strong>
            <span style="color:#A8C880;"> Active (Mock)</span><br>
            <strong style="color:#C8D8A0;">TTS Engine:</strong>
            <span style="color:#A8C880;"> gTTS v2.4</span><br>
            <strong style="color:#C8D8A0;">Fleet Status:</strong>
            <span style="color:{'#FF6B6B' if st.session_state.get('hazard_active') else '#A8C880'};
                         font-weight:700;"> {hazard_status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
# SECTION 7: MAIN APP HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="app-header">
        <div>
            <h1>🌾 Agri-Logistics IDAS</h1>
            <p>Intelligent Driver Assistance System &nbsp;·&nbsp;
               Sindh Agricultural Supply Chain &nbsp;·&nbsp;
               Trilingual NLP + Context-Aware Safety</p>
        </div>
        <div class="header-right">
            <div class="header-badge">PHASE 3 · FULL SYSTEM</div>
            <div class="header-author">
                Lokesh Kumar &nbsp;·&nbsp; 2k22-SE-42 &nbsp;·&nbsp;
                Sindh Agriculture University, Tandojam
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════
# SECTION 8: TABS
# ═══════════════════════════════════════════════════════════════════

tab_corp, tab_driver = st.tabs(
    ["🏢 Corporate Dashboard", "🚚 Driver Interface"]
)


# ───────────────────────────────────────────────────────────────────
# TAB 1 — CORPORATE DASHBOARD
# ───────────────────────────────────────────────────────────────────
with tab_corp:

    # ── KPI Metric Cards ──────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4, gap="medium")

    kpis = [
        ("ACTIVE TRUCKS",  "24",  "↑ 3 since yesterday",  "#4A7C2F", "positive"),
        ("DELIVERIES",     "138", "↑ 12% vs last week",   "#4A7C2F", "positive"),
        ("IN TRANSIT",     "17",  "On scheduled routes",  "#6B5E2F", "neutral"),
        ("HAZARDS",        "1",   "⚠ Requires attention", "#8A3A1A", "negative"),
    ]

    for col, (label, value, delta, accent, delta_cls) in zip(
        [k1, k2, k3, k4], kpis
    ):
        with col:
            st.markdown(
                f"""
                <div class="metric-card" style="border-left-color:{accent};">
                    <h3>{label}</h3>
                    <p class="metric-value">{value}</p>
                    <p class="metric-delta {delta_cls}">{delta}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='agri-hr' style='margin:22px 0;'>", unsafe_allow_html=True)

    # ── Hazard Banner (shown when driver has reported a hazard) ───
    if st.session_state.get("hazard_active", False):
        st.markdown(
            f"""
            <div class="hazard-banner">
                <div class="hazard-banner-icon">🚨</div>
                <div class="hazard-banner-text">
                    HIGH-PRIORITY ALERT — Driver TRK-119 Reported a Hazard
                    <small>Translated message: {st.session_state.get("last_hazard_msg", "")}</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("✅ Acknowledge & Dismiss Hazard", type="secondary"):
            st.session_state["hazard_active"]   = False
            st.session_state["last_hazard_msg"] = ""
            st.rerun()

    # ── Map + Fleet layout ────────────────────────────────────────
    col_map, col_fleet = st.columns([1.6, 1], gap="large")

    with col_map:
        st.markdown("<div class='section-card'><h4>🗺️ Live Fleet Map</h4>", unsafe_allow_html=True)

        # Check if route data is loaded and successful in session state. If not, fetch it.
        if "route_data" not in st.session_state or not st.session_state["route_data"].get("success", False):
            with st.spinner("Calculating true-road network route via OSRM…"):
                st.session_state["route_data"] = get_osrm_route()
        
        route_data = st.session_state["route_data"]

        if route_data["success"]:
            plot_route_on_map(route_geometry=route_data["geometry"])

            # Store route data in session state for the Driver tab
            st.session_state["route_geometry"]      = route_data["geometry"]
            st.session_state["route_instructions"]  = route_data["instructions"]
            st.session_state["route_distance_km"]   = route_data["distance_km"]
            st.session_state["route_duration_min"]  = route_data["duration_min"]
            st.session_state["route_loaded"]        = True
            st.session_state["route_fallback"]      = False

            # Distance / duration info badges
            dist = route_data["distance_km"]
            dur  = route_data["duration_min"]
            st.markdown(
                f"""
                <div class="route-info-row">
                    <div class="route-badge">📏 {dist} km</div>
                    <div class="route-badge">⏱️ ~{dur} min est.</div>
                    <div class="route-badge">📍 Mithi → Hyderabad</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Network fallback — show marker-only map
            st.warning(
                f"⚠️ OSRM routing unavailable — showing fallback map. "
                f"Reason: {route_data['error']}"
            )
            plot_fallback_map()
            
            st.session_state["route_geometry"]      = None
            st.session_state["route_instructions"]  = ["OSRM routing unavailable — showing fallback map."]
            st.session_state["route_distance_km"]   = None
            st.session_state["route_duration_min"]  = None
            st.session_state["route_loaded"]        = True
            st.session_state["route_fallback"]      = True

        st.markdown("</div>", unsafe_allow_html=True)

    with col_fleet:
        # Fleet status
        st.markdown(
            """
            <div class="section-card">
                <h4>🚛 Fleet Status</h4>
                <p style="color:#4A5C3A; font-size:0.85rem;">
                    TRK-101 &nbsp;<span class="pill pill-green">On Route</span>
                </p>
                <p style="color:#4A5C3A; font-size:0.85rem;">
                    TRK-115 &nbsp;<span class="pill pill-orange">Delayed</span>
                </p>
                <p style="color:#4A5C3A; font-size:0.85rem;">
                    TRK-119 &nbsp;<span class="pill pill-green">On Route</span>
                </p>
                <p style="color:#4A5C3A; font-size:0.85rem;">
                    TRK-204 &nbsp;<span class="pill pill-blue">Loading</span>
                </p>
                <p style="color:#4A5C3A; font-size:0.85rem;">
                    TRK-307 &nbsp;<span class="pill pill-red">Hazard</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Corporate Chat Interface ────────────────────────────────
        st.markdown(
            "<div class='section-card'>"
            "<h4>💬 Dispatch Chat (English View)</h4>",
            unsafe_allow_html=True,
        )
        _render_chat(
            messages=st.session_state.chat_messages,
            view="corporate",
            height=240,
        )
        # Input row — text_input + button (works reliably inside any column)
        corp_inp_col, corp_btn_col = st.columns([5, 1], gap="small")
        with corp_inp_col:
            corp_text = st.text_input(
                "corp_label",
                placeholder="Message TRK-119 driver (English)…",
                label_visibility="collapsed",
                key="corp_text_input",
            )
        with corp_btn_col:
            corp_send = st.button(
                "Send", key="corp_send_btn", use_container_width=True
            )
        if corp_send and corp_text.strip():
            st.session_state.chat_messages.append(
                {
                    "role":        "corporate",
                    "original":    corp_text.strip(),
                    "english":     corp_text.strip(),
                    "source_lang": "English",
                }
            )
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)



# ───────────────────────────────────────────────────────────────────
# TAB 2 — DRIVER INTERFACE
# ───────────────────────────────────────────────────────────────────
with tab_driver:

    lang_flag  = LANG_FLAG.get(st.session_state["driver_language"], "🟢")
    cargo_cls, cargo_lbl = CARGO_LABELS.get(
        st.session_state["cargo_type"], CARGO_LABELS["Standard"]
    )

    # ── Driver identity panel ──────────────────────────────────────
    st.markdown(
        f"""
        <div class="driver-panel">
            <h2>👤 {st.session_state["driver_name"]}</h2>
            <p class="sub">{st.session_state["driver_id"]} &nbsp;·&nbsp;
               {st.session_state["vehicle_id"]}</p>
            <div class="driver-info-row">
                <div class="driver-info-item">
                    <label>Route</label>
                    <span>{st.session_state["current_route"]}</span>
                </div>
                <div class="driver-info-item">
                    <label>Language</label>
                    <span>{lang_flag} {st.session_state["driver_language"]}</span>
                </div>
                <div class="driver-info-item">
                    <label>Cargo</label>
                    <span class="{cargo_cls}">{cargo_lbl}</span>
                </div>
                <div class="driver-info-item">
                    <label>Time</label>
                    <span>{"🌙 Night" if st.session_state["time_of_day"] == "Night" else "☀️ Day"}</span>
                </div>
                <div class="driver-info-item">
                    <label>Weather</label>
                    <span>{"🌧️ Rain" if st.session_state["weather"] == "Rain" else "☀️ Clear"}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Context simulator dropdowns ────────────────────────────────
    col_lang, col_cargo, col_time, col_weather = st.columns(4, gap="medium")

    with col_lang:
        selected_lang = st.selectbox(
            "🌐 Language",
            options=LANGUAGES,
            index=LANGUAGES.index(st.session_state["driver_language"]),
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
            key="_cargo_select",
        )
        if selected_cargo != st.session_state["cargo_type"]:
            st.session_state["cargo_type"] = selected_cargo
            st.rerun()

    with col_time:
        selected_time = st.selectbox(
            "⏱️ Time (Simulate)",
            options=TIME_OPTS,
            index=TIME_OPTS.index(st.session_state["time_of_day"]),
            key="_time_select",
        )
        if selected_time != st.session_state["time_of_day"]:
            st.session_state["time_of_day"] = selected_time
            st.rerun()

    with col_weather:
        selected_weather = st.selectbox(
            "☁️ Weather (Simulate)",
            options=WEATHER_OPTS,
            index=WEATHER_OPTS.index(st.session_state["weather"]),
            key="_weather_select",
        )
        if selected_weather != st.session_state["weather"]:
            st.session_state["weather"] = selected_weather
            st.rerun()

    st.markdown("<hr class='agri-hr'>", unsafe_allow_html=True)

    # ── Dynamic Context-Aware Safety Alert Panel ───────────────────
    css_class, alert_title, alert_message, eng_title = get_safety_context(
        cargo_type  = st.session_state["cargo_type"],
        time_of_day = st.session_state["time_of_day"],
        weather     = st.session_state["weather"],
        language    = st.session_state["driver_language"],
    )

    # Map icon from title prefix
    icon_map = {
        "⛔":  "⛔",
        "🛑":  "🛑",
        "🍅":  "🍅",
        "🌧️": "🌧️",
        "🌙":  "🌙",
        "🌦️": "🌦️",
        "ℹ️": "ℹ️",
    }
    alert_icon = "ℹ️"
    for prefix, icon in icon_map.items():
        if alert_title.startswith(prefix):
            alert_icon = icon
            break

    st.markdown(
        f"""
        <div class="safety-alert {css_class}">
            <div class="safety-icon">{alert_icon}</div>
            <div class="safety-text">
                <h5>{alert_title}</h5>
                <p>{alert_message}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Main driver columns ────────────────────────────────────────
    col_nav, col_assist = st.columns([1.4, 1], gap="large")

    with col_nav:
        st.markdown(
            """
            <div class="section-card">
                <h4>🗺️ Navigation View</h4>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("route_loaded", False):
            # Use pure HTML rendering — avoids all st_folium duplicate-key
            # conflicts that occur when two maps exist in the same session.
            if st.session_state.get("route_fallback", False):
                map_html = get_fallback_map_html(map_height_px=290)
            else:
                map_html = get_route_map_html(
                    route_geometry=st.session_state["route_geometry"],
                    map_height_px=290,
                )
            components.html(map_html, height=295, scrolling=False)
        else:
            st.markdown(
                """
                <div class="nav-placeholder">
                    <span style="font-size:2rem;">🧭</span>
                    <span>Turn-by-turn navigation map</span>
                    <span style="font-size:0.72rem; color:#B0A890;">
                        Load the Corporate Dashboard map first to enable this view
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_assist:
        target_lang = st.session_state["driver_language"]

        st.markdown(
            f"<div class='section-card'>"
            f"<h4>💬 Dispatch Chat ({lang_flag} {target_lang})</h4>",
            unsafe_allow_html=True,
        )
        _render_chat(
            messages=st.session_state.chat_messages,
            view="driver",
            target_lang=target_lang,
            height=210,
        )
        # Input row — text_input + button (works reliably inside any column)
        drv_inp_col, drv_btn_col = st.columns([5, 1], gap="small")
        with drv_inp_col:
            drv_text = st.text_input(
                "drv_label",
                placeholder=f"Report hazard in {target_lang}…",
                label_visibility="collapsed",
                key="drv_text_input",
            )
        with drv_btn_col:
            drv_send = st.button(
                "Send", key="drv_send_btn", use_container_width=True
            )
        if drv_send and drv_text.strip():
            english_translation = mock_translate(drv_text.strip(), "English")
            hazard_detected     = is_hazard_message(drv_text.strip())
            st.session_state.chat_messages.append(
                {
                    "role":        "driver",
                    "original":    drv_text.strip(),
                    "english":     english_translation,
                    "source_lang": target_lang,
                }
            )
            if hazard_detected:
                st.session_state["hazard_active"]   = True
                st.session_state["last_hazard_msg"] = english_translation
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


    # ── Audio Guidance + Telemetry row ────────────────────────────
    col_audio, col_tele = st.columns(2, gap="large")

    with col_audio:
        st.markdown(
            "<div class='section-card'><h4>🔊 Audio Guidance</h4>",
            unsafe_allow_html=True,
        )
        instructions = st.session_state.get("route_instructions", [])

        if instructions and len(instructions) > 1:
            next_turn = instructions[1]
            st.markdown(
                f"""
                <div style="background:#F0EDE6; border-radius:8px; padding:10px 14px;
                            font-size:0.83rem; color:#2D3A1F; margin-bottom:12px;
                            border-left:3px solid #4A7C2F;">
                    <strong>Next:</strong> {next_turn}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"🔊 Play in {st.session_state['driver_language']}",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Generating audio…"):
                    result = generate_voice_advisory(
                        base_instruction=next_turn,
                        language=st.session_state["driver_language"],
                        cargo_type=st.session_state["cargo_type"],
                    )

                if result["success"]:
                    st.success(
                        f"**{result['language']}:** {result['text']}"
                    )
                    # Wrap bytes in BytesIO for st.audio — no autoplay=True
                    audio_buf = io.BytesIO(result["audio_bytes"])
                    st.audio(audio_buf, format="audio/mp3")
                    st.caption(result["transcript"])
                else:
                    st.error(result["error"])
        else:
            st.info("⚠️ Load the map in the Corporate Dashboard to enable audio guidance.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_tele:
        st.markdown(
            """
            <div class="section-card">
                <h4>📡 Vehicle Telemetry</h4>
                <div class="tele-row">
                    <span class="tele-label">Speed</span>
                    <span class="tele-pending">— km/h (OBD Phase 2)</span>
                </div>
                <div class="tele-row">
                    <span class="tele-label">Engine Temp</span>
                    <span class="tele-pending">— °C (OBD Phase 2)</span>
                </div>
                <div class="tele-row">
                    <span class="tele-label">Fuel Level</span>
                    <span class="tele-pending">— % (OBD Phase 2)</span>
                </div>
                <div class="tele-row">
                    <span class="tele-label">RPM</span>
                    <span class="tele-pending">— (OBD Phase 2)</span>
                </div>
                <div class="tele-row">
                    <span class="tele-label">Door Status</span>
                    <span class="tele-value" style="color:#4A7C2F;">🟢 Closed</span>
                </div>
                <div class="tele-row" style="border:none;">
                    <span class="tele-label">GPS Signal</span>
                    <span class="tele-value" style="color:#4A7C2F;">🟢 Strong</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════
# SECTION 9: IEEE-STYLE ACADEMIC FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="ieee-footer">
        <div class="footer-left">
            <div class="footer-title">📄 Research Citation</div>
            <div class="footer-citation">
                <em>Kumar, L.</em> (2024). "Bridging the Digital Literacy Gap in
                Rural Agri-Logistics: A Trilingual, Context-Aware Intelligent Driver
                Assistance System for the Sindh Agricultural Supply Chain."
                <em>Proceedings of the Sindh Agriculture University Research Symposium.</em>
                Tandojam, Pakistan.
                <span class="footer-dot"></span>
                Student ID: 2k22-SE-42
                <span class="footer-dot"></span>
                2K22-SE-42@student.sau.edu.pk
            </div>
        </div>
        <div class="footer-right">
            Agri-Logistics IDAS<br>
            Phase 3 Prototype<br>
            Sindh Agriculture University<br>
            <span style="color:#D4AF37; font-weight:700;">© 2024 Lokesh Kumar</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
