"""
voice_advisory.py — Agri-Logistics IDAS
=========================================
Production-grade multilingual voice guidance layer for the Intelligent
Driver Assistance System (IDAS). Phase 3 edition.
Author      : Lokesh Kumar
Student ID  : 2k22-SE-42
Email       : 2K22-SE-42@student.sau.edu.pk
Institution : Sindh Agriculture University, Tandojam
Public API
----------
    result = generate_voice_advisory(base_instruction, language, cargo_type)
    Result dict keys:
        success     : bool   — False if TTS generation failed
        text        : str    — The romanised text that was spoken
        language    : str    — The target language ("Sindhi", "Urdu", "Dhatki")
        cargo_type  : str    — The cargo type passed in
        audio_bytes : bytes  — Raw MP3 audio bytes (pass to st.audio)
        transcript  : str    — Human-readable transcript line for display
        error       : str    — Error message (only set when success=False)
Streamlit usage
---------------
    from voice_advisory import generate_voice_advisory
    result = generate_voice_advisory(
        base_instruction = "Turn left onto National Highway 8 (12.0 km)",
        language         = "Urdu",
        cargo_type       = "Fragile / Tomatoes",
    )
    if result["success"]:
        import io
        st.audio(io.BytesIO(result["audio_bytes"]), format="audio/mp3")
        st.caption(result["transcript"])
Caching
-------
    The heavy gTTS HTTP call is wrapped in `@st.cache_data` so repeated
    calls with identical (text, lang_code, slow) arguments return the
    cached bytes immediately without additional network requests.
Dependencies
------------
    pip install gtts streamlit
"""
import io
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
PHRASE_BOOK: dict = {
    # ── Departure ──────────────────────────────────────────────
    "Head straight": {
        "Sindhi":  "Seedho vanj",
        "Urdu":    "Seedha chalo",
        "Dhatki":  "Seedha halo",
    },
    "Head": {
        "Sindhi":  "vanjo",
        "Urdu":    "Chalo",
        "Dhatki":  "halo",
    },
    # ── Turns ───────────────────────────────────────────────────
    "Turn left": {
        "Sindhi":  "Khabbey phiro",
        "Urdu":    "Baayein muro",
        "Dhatki":  "undhe hath the phiro",
    },
    "Turn right": {
        "Sindhi":  "Saje moro",
        "Urdu":    "Daayein muro",
        "Dhatki":  "Sindhe hath the moro",
    },
    "Turn slight left": {
        "Sindhi":  "Thoro khabbey moro",
        "Urdu":    "Thoda baayein",
        "Dhatki":  "Thoro khabay moro",
    },
    "Turn slight right": {
        "Sindhi":  "Thoro sajey moro",
        "Urdu":    "Thoda daayein",
        "Dhatki":  "Thoro sajey moro",
    },
    "Turn sharp left": {
        "Sindhi":  "Tikkhi khabbe moro",
        "Urdu":    "Teekha baayein muro",
        "Dhatki":  "Tikkho khabey phir",
    },
    "Turn sharp right": {
        "Sindhi":  "jaldi saje moro",
        "Urdu":    "Teekha daayein muro",
        "Dhatki":  "jaldi sajey phirao",
    },
    "Turn U-turn": {
        "Sindhi":  "U-turn karo",
        "Urdu":    "U-turn len",
        "Dhatki":  "U-turn karo",
    },
    # ── Continuing ──────────────────────────────────────────────
    "Continue straight": {
        "Sindhi":  "Seedho halda wanjo",
        "Urdu":    "Seedha jaari rakhen",
        "Dhatki":  "Seedho halta raho",
    },
    "Continue": {
        "Sindhi":  "jaari rakho",
        "Urdu":    "Jaari rakhen",
        "Dhatki":  "halta jao",
    },
    "Continue onto": {
        "Sindhi":  "Aage wanjio",
        "Urdu":    "Aage badhein",
        "Dhatki":  "Aagya halo",
    },
    # ── Merges and ramps ────────────────────────────────────────
    "Merge onto": {
        "Sindhi":  "Sadak te bhera thio",
        "Urdu":    "Sadak par shamil hon",
        "Dhatki":  "Raah mein bhera thiyo",
    },
    "Take ramp onto": {
        "Sindhi":  "Ramp te acho",
        "Urdu":    "Ramp par aayein",
        "Dhatki":  "Ramp te aao",
    },
    "Take exit onto": {
        "Sindhi":  "Exit khe pakaro",
        "Urdu":    "Exit lein",
        "Dhatki":  "Bahar jao",
    },
    "Take fork onto": {
        "Sindhi":  "Kaanta ri taraf vanjo",
        "Urdu":    "Kaante ki taraf jaayein",
        "Dhatki":  "Kaante ri taraf jao",
    },
    # ── Junctions ───────────────────────────────────────────────
    "Enter roundabout": {
        "Sindhi":  "Gol chakkar je andar vanjo",
        "Urdu":    "Gol chakkar mein daakhil hon",
        "Dhatki":  "Gol chakkar re andar jao",
    },
    "At end of road, turn": {
        "Sindhi":  "road jo aakhir te gaadi, moro",
        "Urdu":    "Sadak ke aakhir mein muren",
        "Dhatki":  "Raste re aakhir main gaadi, phirao",
    },
    # ── Arrival ─────────────────────────────────────────────────
    "Arrive at destination": {
        "Sindhi":  "Manzil te pahunchi wya. Safar pooro thiyo.",
        "Urdu":    "Manzil par pahunch gaye. Safar mukammal hua.",
        "Dhatki":  "manzil te pohche gya. Safar khatam thiyo.",
    },
}
# ─────────────────────────────────────────────────────────────────
# FRAGILE CARGO SUFFIX
# ─────────────────────────────────────────────────────────────────
# This sentence is appended to every advisory when cargo_type is
# CARGO_FRAGILE.  The slow=True flag in gTTS is also activated for
# fragile cargo to make the speech clearer and more deliberate.
FRAGILE_SUFFIX: dict = {
    "Sindhi":  "Nazuk maal aahay, ahista halo",
    "Urdu":    "Nazuk maal hai, aahista chalo",
    "Dhatki":  "Nazuk bojh hai, aastay halo",
}
# ─────────────────────────────────────────────────────────────────
# gTTS LANGUAGE CODE MAP
# ─────────────────────────────────────────────────────────────────
# gTTS uses BCP-47 language codes.  Sindhi (sd) and Dhatki have
# limited or no dedicated TTS support, so we route them through
# Urdu (ur) which shares much of the phonetic vocabulary and produces
# intelligible output for Roman-script Sindhi/Dhatki phrases.
#
# Language code reference:
#   https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
GTTS_LANG_CODE: dict = {
    "Sindhi":  "ur",   # closest available TTS; ur phonetics cover most Sindhi
    "Urdu":    "ur",   # native TTS
    "Dhatki":  "hi",   # Dhatki shares phonetics with Hindi/Rajasthani
}
# ─────────────────────────────────────────────────────────────────
# HELPER — match the longest phrase-book key inside an instruction
# ─────────────────────────────────────────────────────────────────
def _match_phrase(instruction: str) -> str | None:
    """
    Return the phrase-book key that best matches the start of `instruction`.
    We sort keys by descending length so "Turn sharp left" is tested
    before "Turn" and "Turn left", preventing premature short matches.
    """
    for key in sorted(PHRASE_BOOK.keys(), key=len, reverse=True):
        if instruction.startswith(key):
            return key
    return None
# ─────────────────────────────────────────────────────────────────
# HELPER — translate a single OSRM instruction to target language
# ─────────────────────────────────────────────────────────────────
def _translate_instruction(instruction: str, language: str) -> str:
    """
    Translate one OSRM plain-English instruction into the target language.
    Strategy:
      1. Match the longest phrase-book key at the start of the instruction.
      2. Extract any trailing road-name / distance suffix that was not
         matched by the phrase key.
      3. Return: "<translated_verb> <untranslated_suffix>".
         Road names and distances are intentionally kept in English/Roman
         because they are universally recognised by drivers regardless of
         language, and translation would introduce ambiguity.
    Falls back gracefully to the original English string if no match.
    """
    if language not in GTTS_LANG_CODE:
        return instruction     # safety guard — return English unchanged
    matched_key = _match_phrase(instruction)
    if not matched_key:
        return instruction     # no phrase-book entry — keep English
    # Retrieve the translated verb phrase
    translations = PHRASE_BOOK[matched_key]
    translated_verb = translations.get(language, instruction)
    # Extract the untranslated suffix (road name, distance, etc.)
    suffix = instruction[len(matched_key):].strip()
    if suffix:
        return f"{translated_verb} — {suffix}"
    return translated_verb
# ─────────────────────────────────────────────────────────────────
# CACHED TTS AUDIO GENERATOR
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _get_cached_audio_bytes(text: str, lang_code: str, slow: bool) -> bytes | None:
    """
    Generate TTS audio via gTTS and return the raw MP3 bytes.
    This function is decorated with @st.cache_data so that repeated
    calls with the same (text, lang_code, slow) arguments return the
    already-generated bytes without making another gTTS HTTP request.
    This dramatically reduces latency on re-renders and re-runs.
    Parameters
    ----------
    text      : The romanised text to synthesise.
    lang_code : BCP-47 language code (e.g. "ur", "hi").
    slow      : If True, gTTS generates slower speech (used for fragile cargo).
    Returns
    -------
    bytes — raw MP3 audio data, or None if gTTS raised an exception.
    """
    try:
        tts = gTTS(text=text, lang=lang_code, slow=slow)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except gTTSError as exc:
        logger.error("gTTS synthesis error: %s", exc)
        return None
    except Exception as exc:
        logger.error("Unexpected TTS error: %s", exc)
        return None
# ─────────────────────────────────────────────────────────────────
# PUBLIC FUNCTION — generate_voice_advisory
# ─────────────────────────────────────────────────────────────────
def generate_voice_advisory(
    base_instruction: str,
    language:         str = "Urdu",
    cargo_type:       str = "Standard",
) -> dict:
    """
    Translate a routing instruction and synthesise it as MP3 audio.
    Parameters
    ----------
    base_instruction : Plain-English OSRM instruction string, e.g.
                       "Turn left onto National Highway 8 (12.0 km)".
    language         : Target language — one of "Sindhi", "Urdu", "Dhatki".
                       Defaults to "Urdu" if an unrecognised value is passed.
    cargo_type       : Cargo type string from the Streamlit selectbox.
                       When equal to CARGO_FRAGILE, a safety suffix is
                       appended and speech rate is slowed.
    Returns
    -------
    dict:
        success     : bool  — True if audio was generated successfully.
        text        : str   — The final romanised text that was synthesised.
        language    : str   — The target language that was used.
        cargo_type  : str   — The cargo_type argument that was passed in.
        audio_bytes : bytes — Raw MP3 bytes; None on failure.
        transcript  : str   — Human-readable label for the audio player UI.
        error       : str   — Error description; None on success.
    """
    # ── 1. Normalise language ──────────────────────────────────
    if language not in GTTS_LANG_CODE:
        logger.warning("Unknown language '%s'; defaulting to Urdu.", language)
        language = "Urdu"
    lang_code = GTTS_LANG_CODE[language]
    # ── 2. Translate instruction ───────────────────────────────
    translated_text = _translate_instruction(base_instruction, language)
    # ── 3. Append fragile-cargo safety suffix ─────────────────
    is_fragile = (cargo_type == CARGO_FRAGILE)
    if is_fragile:
        suffix = FRAGILE_SUFFIX.get(language, "")
        if suffix:
            translated_text = f"{translated_text}. {suffix}."
    # ── 4. Choose speech rate ──────────────────────────────────
    # Slow speech for fragile cargo so the driver can process the advisory
    # clearly even in noisy truck cab environments.
    slow = is_fragile
    # ── 5. Generate (or retrieve cached) audio bytes ──────────
    audio_bytes = _get_cached_audio_bytes(translated_text, lang_code, slow)
    if audio_bytes is None:
        return {
            "success":     False,
            "text":        translated_text,
            "language":    language,
            "cargo_type":  cargo_type,
            "audio_bytes": None,
            "transcript":  "",
            "error": (
                "gTTS audio generation failed. This may be a network issue "
                "or a temporary Google TTS service outage. "
                "Check your internet connection and try again."
            ),
        }
    # ── 6. Build transcript label ──────────────────────────────
    cargo_label = "🍅 Fragile" if is_fragile else "📦 Standard"
    transcript  = (
        f"🔊 [{language} · {cargo_label}] — {translated_text}"
    )
    return {
        "success":     True,
        "text":        translated_text,
        "language":    language,
        "cargo_type":  cargo_type,
        "audio_bytes": audio_bytes,
        "transcript":  transcript,
        "error":       None,
    }
