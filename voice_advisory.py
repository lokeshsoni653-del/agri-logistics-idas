"""
voice_advisory.py — Agri-Logistics IDAS
=========================================
Intelligent Driver Advisory System (IDAS) — voice guidance layer.

Public API
----------
    result = generate_voice_advisory(base_instruction, language, cargo_type)
    # result keys: success, text, language, cargo_type, audio_buffer, error

Streamlit usage
---------------
    from voice_advisory import generate_voice_advisory

    result = generate_voice_advisory(
        base_instruction = "Turn left onto National Highway 8 (12.0 km)",
        language         = "Urdu",
        cargo_type       = "Fragile / Tomatoes",
    )
    if result["success"]:
        st.audio(result["audio_buffer"], format="audio/mp3")

Dependencies
------------
    pip install gtts streamlit
"""

import io
import re
import logging

import streamlit as st
from gtts import gTTS, gTTSError

# ─────────────────────────────────────────────────────────────────
# MODULE LOGGER
# ─────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# CARGO TYPE CONSTANT
# ─────────────────────────────────────────────────────────────────

#: Must match the value used in the Streamlit selectbox in the main app.
CARGO_FRAGILE = "Fragile / Tomatoes"

# ─────────────────────────────────────────────────────────────────
# PHRASE BOOK  (English → Romanised local script)
# ─────────────────────────────────────────────────────────────────
# Keys are the English maneuver-verb prefixes produced by routing.py.
# Each key maps to a dict of {language: romanised translation}.
#
# Design notes:
#   • Sindhi  — uses common Sindhi Roman spellings spoken in Tharparkar
#   • Urdu    — standard Urdu Roman transliteration
#   • Dhatki  — a Rajasthani dialect spoken in Tharparkar; approximated
#               here with Roman script for TTS input
#
# The lookup uses longest-key-first matching so "Turn left" does not
# shadow "Turn" before "Take ramp onto" shadows "Take".
#
# Extend this dict as new OSRM maneuver types are encountered.
# ─────────────────────────────────────────────────────────────────

PHRASE_BOOK: dict[str, dict[str, str]] = {

    # ── Departure ──────────────────────────────────────────────
    "Head straight": {
        "Sindhi":  "Seedho halo",
        "Urdu":    "Seedha chalo",
        "Dhatki":  "Seedho vanj",
    },
    "Head": {
        "Sindhi":  "Halo",
        "Urdu":    "Chalo",
        "Dhatki":  "Vanj",
    },

    # ── Turns ───────────────────────────────────────────────────
    "Turn left": {
        "Sindhi":  "Khabbe moro",
        "Urdu":    "Baayein muro",
        "Dhatki":  "Khabey phir",
    },
    "Turn right": {
        "Sindhi":  "Saje moro",
        "Urdu":    "Daayein muro",
        "Dhatki":  "Sajey phir",
    },
    "Turn slight left": {
        "Sindhi":  "Thoro khabbe",
        "Urdu":    "Thoda baayein",
        "Dhatki":  "Thoro khabey",
    },
    "Turn slight right": {
        "Sindhi":  "Thoro saje",
        "Urdu":    "Thoda daayein",
        "Dhatki":  "Thoro sajey",
    },
    "Turn sharp left": {
        "Sindhi":  "Tikkhi khabbe moro",
        "Urdu":    "Teekha baayein muro",
        "Dhatki":  "Tikkho khabey phir",
    },
    "Turn sharp right": {
        "Sindhi":  "Tikkhi saje moro",
        "Urdu":    "Teekha daayein muro",
        "Dhatki":  "Tikkho sajey phir",
    },
    "Turn U-turn": {
        "Sindhi":  "U-turn karo",
        "Urdu":    "U-turn len",
        "Dhatki":  "U-turn karo",
    },

    # ── Continuing ──────────────────────────────────────────────
    "Continue straight": {
        "Sindhi":  "Seedho jaari rakho",
        "Urdu":    "Seedha jaari rakhen",
        "Dhatki":  "Seedho chalte raho",
    },
    "Continue": {
        "Sindhi":  "Jaari rakho",
        "Urdu":    "Jaari rakhen",
        "Dhatki":  "Chalte raho",
    },
    "Continue onto": {
        "Sindhi":  "Aage wanjio",
        "Urdu":    "Aage badhein",
        "Dhatki":  "Aagey vanj",
    },

    # ── Merges and ramps ────────────────────────────────────────
    "Merge onto": {
        "Sindhi":  "Sadak te shamil thio",
        "Urdu":    "Sadak par shamil hon",
        "Dhatki":  "Raah mein mil",
    },
    "Take ramp onto": {
        "Sindhi":  "Ramp khe pakaro",
        "Urdu":    "Ramp par aayein",
        "Dhatki":  "Ramp pakaro",
    },
    "Take exit onto": {
        "Sindhi":  "Exit khe pakaro",
        "Urdu":    "Exit lein",
        "Dhatki":  "Bahar niklo",
    },
    "Take fork onto": {
        "Sindhi":  "Kaanta varo",
        "Urdu":    "Kaante ki taraf jaayein",
        "Dhatki":  "Kaanto vanj",
    },

    # ── Junctions ───────────────────────────────────────────────
    "Enter roundabout": {
        "Sindhi":  "Gol chakkar andar",
        "Urdu":    "Gol chakkar mein daakhil hon",
        "Dhatki":  "Gol chakkar andar",
    },
    "At end of road, turn": {
        "Sindhi":  "Sadak khatam, moro",
        "Urdu":    "Sadak ke aakhir mein muren",
        "Dhatki":  "Raah khatam, phir",
    },

    # ── Arrival ─────────────────────────────────────────────────
    "Arrive at destination": {
        "Sindhi":  "Manzil te pahuncha. Safar mukliyo.",
        "Urdu":    "Manzil par pahunch gaye. Safar mukammal hua.",
        "Dhatki":  "Thaur te pahuncha. Safar khatam.",
    },
}


# ─────────────────────────────────────────────────────────────────
# FRAGILE CARGO SUFFIX
# ─────────────────────────────────────────────────────────────────
# This sentence is appended to every advisory when cargo_type is
# CARGO_FRAGILE.  The slow=True flag in gTTS is also activated for
# fragile cargo to make the speech clearer and more deliberate.

FRAGILE_SUFFIX: dict[str, str] = {
    "Sindhi":  "Nazuk maal aahay, ahista halo",
    "Urdu":    "Nazuk maal hai, aahista chalo",
    "Dhatki":  "Nazuk bojh aahe, ahista vanj",
}


# ─────────────────────────────────────────────────────────────────
# gTTS LANGUAGE CODE MAP
# ─────────────────────────────────────────────────────────────────
# gTTS uses BCP-47 language codes.  Sindhi (sd) and Dhatki have
# limited or no dedicated TTS support, so we route them through
# Urdu ('ur') which produces the most intelligible result for
# Romanised Sindhi/Dhatki text.

GTTS_LANG_CODE: dict[str, str] = {
    "Sindhi":  "ur",   # closest supported TTS accent
    "Urdu":    "ur",   # native
    "Dhatki":  "ur",   # closest supported TTS accent
}

# Regex to strip leading English prepositions from the remainder of
# an instruction phrase so translated output reads more naturally.
_PREPOSITION_RE = re.compile(
    r"^(onto|on|at|into|towards?|toward)\s+", re.IGNORECASE
)


# ─────────────────────────────────────────────────────────────────
# PRIVATE HELPER — translate one phrase
# ─────────────────────────────────────────────────────────────────

def _translate_phrase(english_phrase: str, language: str) -> str:
    """
    Look up the best matching key in PHRASE_BOOK and return the
    translated string with any road name / distance appended.

    Matching strategy
    -----------------
    Keys are sorted longest-first so more-specific entries (e.g.
    "Turn sharp left") are checked before shorter ones ("Turn left",
    "Turn").  The first prefix match wins.

    Remainder handling
    ------------------
    After stripping the matched key, any leftover text (road name,
    distance) is cleaned of leading English prepositions and joined
    with a dash:
        "Turn left onto NH-8 (12 km)"
        → key match: "Turn left"
        → remainder: "onto NH-8 (12 km)"  →  strip "onto"  →  "NH-8 (12 km)"
        → result: "Baayein muro - NH-8 (12 km)"

    Fallback
    --------
    If no key matches, the original English phrase is returned so the
    driver still hears something intelligible.

    Parameters
    ----------
    english_phrase : str  — one instruction string from routing.py
    language       : str  — "Sindhi", "Urdu", or "Dhatki"

    Returns
    -------
    str — translated (or original-English fallback) instruction
    """
    # Sort longest key first to avoid short keys shadowing long ones
    sorted_keys = sorted(PHRASE_BOOK.keys(), key=len, reverse=True)

    for key in sorted_keys:
        if english_phrase.lower().startswith(key.lower()):
            translations = PHRASE_BOOK[key]

            # Get the translated verb/phrase, fall back to English key
            translated_base = translations.get(language, key)

            # Anything after the matched key is road name + distance
            remainder = english_phrase[len(key):].strip()

            # Strip leading English prepositions ("onto", "on", "at", …)
            remainder = _PREPOSITION_RE.sub("", remainder).strip()

            if remainder:
                return f"{translated_base} - {remainder}"
            return translated_base

    # No match found — return the original English instruction as fallback
    logger.warning("No translation found for %r in language %r", english_phrase, language)
    return english_phrase


# ─────────────────────────────────────────────────────────────────
# PUBLIC FUNCTION — generate_voice_advisory
# ─────────────────────────────────────────────────────────────────

def generate_voice_advisory(
    base_instruction: str,
    language:         str = "Urdu",
    cargo_type:       str = "Standard",
) -> dict:
    """
    Translate a driving instruction into the target language, apply
    cargo-specific modifiers, and synthesise it to an MP3 audio buffer.

    Parameters
    ----------
    base_instruction : str
        One English instruction string as produced by
        ``routing._build_instruction()``.
        Example: "Turn left onto National Highway 8 (12.0 km)"

    language : str
        One of ``"Sindhi"``, ``"Urdu"``, or ``"Dhatki"``.
        Defaults to ``"Urdu"`` — the most widely understood language
        across the Sindh supply-chain corridor.

    cargo_type : str
        One of ``"Standard"`` or ``"Fragile / Tomatoes"``.
        When ``"Fragile / Tomatoes"`` is selected:
          • A language-specific caution phrase is appended to the text.
          • gTTS ``slow=True`` is activated for more deliberate speech.

    Returns
    -------
    dict with the following keys:

        success       : bool
            True if audio was synthesised successfully.

        text          : str
            The final translated text that was sent to gTTS.
            Useful for displaying subtitles alongside the audio player.

        language      : str
            Echo of the requested language parameter.

        cargo_type    : str
            Echo of the cargo_type parameter.

        audio_buffer  : io.BytesIO | None
            In-memory MP3 buffer.  Pass directly to ``st.audio()``.
            None on failure.

        error         : str | None
            Human-readable error message on failure, None on success.

    Raises
    ------
    Does not raise — all errors are returned in the result dict so
    Streamlit can display them without crashing the app.

    Example
    -------
    >>> result = generate_voice_advisory(
    ...     base_instruction = "Turn right onto Hyderabad Bypass (8.0 km)",
    ...     language         = "Sindhi",
    ...     cargo_type       = "Fragile / Tomatoes",
    ... )
    >>> if result["success"]:
    ...     st.caption(result["text"])
    ...     st.audio(result["audio_buffer"], format="audio/mp3")
    ... else:
    ...     st.error(result["error"])
    """

    # ── 1. Validate language ──────────────────────────────────────
    supported_languages = list(GTTS_LANG_CODE.keys())   # ["Sindhi", "Urdu", "Dhatki"]

    if language not in supported_languages:
        return {
            "success":      False,
            "text":         "",
            "language":     language,
            "cargo_type":   cargo_type,
            "audio_buffer": None,
            "error": (
                f"Language '{language}' is not supported. "
                f"Choose from: {', '.join(supported_languages)}."
            ),
        }

    # ── 2. Validate instruction ───────────────────────────────────
    if not base_instruction or not base_instruction.strip():
        return {
            "success":      False,
            "text":         "",
            "language":     language,
            "cargo_type":   cargo_type,
            "audio_buffer": None,
            "error":        "base_instruction must not be empty.",
        }

    # ── 3. Translate the core instruction ────────────────────────
    translated_instruction = _translate_phrase(
        english_phrase=base_instruction.strip(),
        language=language,
    )

    # ── 4. Append fragile-cargo caution phrase ────────────────────
    # When carrying tomatoes or other fragile produce, the driver
    # receives an extra spoken reminder after every navigation step.
    is_fragile = (cargo_type == CARGO_FRAGILE)

    if is_fragile:
        caution_phrase = FRAGILE_SUFFIX.get(language, FRAGILE_SUFFIX["Urdu"])
        final_text = f"{translated_instruction}. {caution_phrase}."
    else:
        final_text = f"{translated_instruction}."

    # ── 5. Synthesise speech with gTTS ────────────────────────────
    # gTTS streams MP3 data from Google's TTS endpoint.
    # We write directly to a BytesIO buffer so no temp files are
    # created on disk — important for stateless Streamlit deployments.
    #
    # slow=True is activated for fragile cargo to produce speech that
    # is slower and clearer, reducing misheard instructions.

    gtts_lang = GTTS_LANG_CODE[language]   # e.g. "ur" for all three languages

    try:
        tts = gTTS(
            text=final_text,
            lang=gtts_lang,
            slow=is_fragile,   # deliberate pacing for fragile-cargo runs
        )

        # Write MP3 bytes into an in-memory buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)

        # Rewind the buffer so st.audio() reads from the beginning
        audio_buffer.seek(0)

        logger.info(
            "Advisory generated | lang=%s | cargo=%s | text=%r",
            language, cargo_type, final_text,
        )

        return {
            "success":      True,
            "text":         final_text,
            "language":     language,
            "cargo_type":   cargo_type,
            "audio_buffer": audio_buffer,
            "error":        None,
        }

    except gTTSError as exc:
        # gTTSError is raised when Google's TTS endpoint is unreachable
        # or returns an error (e.g. network restrictions in some environments).
        error_msg = (
            f"gTTS synthesis failed: {exc}. "
            "Check your internet connection. "
            "The translated text is still available in result['text']."
        )
        logger.error(error_msg)
        return {
            "success":      False,
            "text":         final_text,   # text is still usable even if audio failed
            "language":     language,
            "cargo_type":   cargo_type,
            "audio_buffer": None,
            "error":        error_msg,
        }

    except Exception as exc:
        error_msg = f"Unexpected error during TTS synthesis: {exc}"
        logger.exception(error_msg)
        return {
            "success":      False,
            "text":         final_text,
            "language":     language,
            "cargo_type":   cargo_type,
            "audio_buffer": None,
            "error":        error_msg,
        }


# ─────────────────────────────────────────────────────────────────
# STANDALONE DEMO — run `streamlit run voice_advisory.py` to test
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Page config ──────────────────────────────────────────────
    st.set_page_config(
        page_title="IDAS Voice Advisory — Test",
        page_icon="🔊",
        layout="wide",
    )

    # ── Custom CSS (minimal, consistent with main app) ────────────
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background-color: #F5F2EC; }
        .phrase-row {
            background: #fff; border-radius: 10px; padding: 14px 18px;
            margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        }
        .phrase-row .eng  { color: #5C6B4A; font-size: 0.8rem; margin-bottom: 4px; }
        .phrase-row .trans { color: #1E3A0F; font-size: 0.95rem; font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Header ───────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#2D5016,#4A7C2F);
                    border-radius:12px; padding:20px 28px; margin-bottom:20px;">
            <h1 style="color:#fff; margin:0; font-size:1.6rem;">
                🔊 IDAS Voice Advisory — Module Test
            </h1>
            <p style="color:#C5DFA0; margin:6px 0 0 0; font-size:0.85rem;">
                Tests <code>generate_voice_advisory()</code> interactively
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Input controls ────────────────────────────────────────────
    col_inputs, col_output = st.columns([1, 1.4], gap="large")

    with col_inputs:
        st.subheader("⚙️ Parameters")

        # Instruction text
        instruction = st.text_input(
            "Base Instruction (English)",
            value="Turn left onto National Highway 8 (12.0 km)",
            help="Paste any instruction string from routing.get_osrm_route()",
        )

        # Language
        language = st.selectbox(
            "🌐 Language",
            options=["Sindhi", "Urdu", "Dhatki"],
            index=1,
        )

        # Cargo type
        cargo = st.selectbox(
            "📦 Cargo Type",
            options=["Standard", "Fragile / Tomatoes"],
            index=0,
        )

        generate_btn = st.button(
            "🔊 Generate Advisory", type="primary", use_container_width=True
        )

    # ── Phrase book reference ─────────────────────────────────────
    with col_output:
        st.subheader("📖 Phrase Book Preview")
        st.caption(
            "All translatable verbs available for the selected language. "
            "These are the keys _translate_phrase() matches against."
        )

        # Show only a sample so the UI isn't overwhelming
        sample_keys = [
            "Head straight", "Turn left", "Turn right",
            "Continue straight", "Arrive at destination",
            "Merge onto", "Enter roundabout",
        ]
        for key in sample_keys:
            trans = PHRASE_BOOK.get(key, {}).get(language, "—")
            st.markdown(
                f"""
                <div class="phrase-row">
                    <div class="eng">🇬🇧 {key}</div>
                    <div class="trans">🗣️ {trans}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Generate and display result ───────────────────────────────
    if generate_btn:

        with st.spinner("Synthesising audio …"):
            result = generate_voice_advisory(
                base_instruction=instruction,
                language=language,
                cargo_type=cargo,
            )

        # ── Result summary cards ──────────────────────────────────
        r1, r2, r3 = st.columns(3)
        r1.metric("Language",   result["language"])
        r2.metric("Cargo",      result["cargo_type"])
        r3.metric("Status",     "✅ OK" if result["success"] else "❌ Failed")

        st.divider()

        col_text, col_audio = st.columns([1.2, 1], gap="large")

        with col_text:
            st.subheader("📝 Advisory Text")

            # Original English instruction
            st.markdown("**Original (English):**")
            st.info(instruction)

            # Final translated + cargo-modified text
            st.markdown("**Translated advisory sent to gTTS:**")
            if result["success"]:
                st.success(result["text"])
            else:
                # Even on TTS failure, text is available for subtitles
                st.warning(result["text"] if result["text"] else "—")

            # Show fragile note if applicable
            if cargo == CARGO_FRAGILE:
                st.caption(
                    f"🍅 Fragile suffix appended: "
                    f"*{FRAGILE_SUFFIX.get(language, '')}*"
                )

        with col_audio:
            st.subheader("🔊 Audio Playback")

            if result["success"] and result["audio_buffer"]:
                st.caption("Click ▶ to play the synthesised advisory.")
                # ── st.audio INTEGRATION ────────────────────────
                # Pass the BytesIO buffer directly — no temp file needed.
                # format="audio/mp3" tells Streamlit the MIME type.
                # autoplay=True plays immediately on page load (use
                # with caution in production — can surprise users).
                st.audio(
                    result["audio_buffer"],
                    format="audio/mp3",
                    autoplay=False,
                )
                # Download button so drivers can save the clip
                result["audio_buffer"].seek(0)   # rewind after st.audio reads it
                st.download_button(
                    label="⬇️ Download MP3",
                    data=result["audio_buffer"],
                    file_name="advisory.mp3",
                    mime="audio/mp3",
                    use_container_width=True,
                )
            else:
                # TTS unavailable — show the text prominently instead
                st.error(f"Audio unavailable: {result['error']}")
                st.info(
                    "💡 **Text-only fallback active.**  "
                    "The advisory text above can still be displayed "
                    "to the driver on-screen.",
                    icon=None,
                )

    else:
        # Idle state
        st.info(
            "👆 Set the parameters above and click **Generate Advisory** to test.",
            icon=None,
        )

    # ── Integration guide ─────────────────────────────────────────
    with st.expander("📋 Integration Guide — how to use in the main app"):
        st.code(
            '''
# In agri_logistics_idas.py — Driver Interface tab

from voice_advisory import generate_voice_advisory

# Called once per navigation step (e.g. when the driver taps "Next step")
result = generate_voice_advisory(
    base_instruction = current_step,                  # from get_osrm_route()
    language         = st.session_state["driver_language"],
    cargo_type       = st.session_state["cargo_type"],
)

# Display translated text as a subtitle
st.caption(result["text"])

# Play the audio — works directly with BytesIO, no temp files
if result["success"]:
    st.audio(result["audio_buffer"], format="audio/mp3", autoplay=True)
else:
    st.warning(f"Audio unavailable: {result['error']}")
            ''',
            language="python",
        )
