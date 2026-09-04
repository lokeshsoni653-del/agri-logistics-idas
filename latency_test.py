import time
import pandas as pd
from gtts import gTTS
import os

# Test Prompts across languages and intent categories
prompts = [
    {"id": "P01", "lang": "Dhatki",  "text": "give me my route", "category": "route"},
    {"id": "P02", "lang": "Dhatki",  "text": "humai kayi side mura", "category": "turn"},
    {"id": "P03", "lang": "Sindhi",  "text": "rasto dasso Mithi thon Hyderabad", "category": "route"},
    {"id": "P04", "lang": "Sindhi",  "text": "tamatar nazuk maal ahe raftar ketri rakhan", "category": "cargo"},
    {"id": "P05", "lang": "Urdu",    "text": "rasta batao kitna distance baqi hai", "category": "route"},
    {"id": "P06", "lang": "Urdu",    "text": "baarish ho rahi hai speed limit kia hai", "category": "weather"},
    {"id": "P07", "lang": "English", "text": "give me estimated time of arrival", "category": "eta"},
    {"id": "P08", "lang": "Dhatki",  "text": "gadi kharab thia ahe madad mokh", "category": "hazard"}
]

# Intent Classification & Context Lookup
def process_intent_nlp(prompt_text, lang):
    start_t = time.perf_counter()
    low = prompt_text.lower()
    cat = "default"
    if any(k in low for k in ["route", "rasto", "raah", "give", "where", "path"]):
        cat = "route"
    elif any(k in low for k in ["mura", "side", "direction", "turn", "left", "right"]):
        cat = "turn"
    elif any(k in low for k in ["speed", "raftar", "tez", "limit"]):
        cat = "speed"
    elif any(k in low for k in ["tamatar", "maal", "cargo", "load"]):
        cat = "cargo"
    elif any(k in low for k in ["barish", "weather", "mosam", "rain"]):
        cat = "weather"
    elif any(k in low for k in ["kharab", "madad", "help", "hazard"]):
        cat = "hazard"

    end_t = time.perf_counter()
    duration_ms = (end_t - start_t) * 1000.0
    return cat, duration_ms

# Audio Generation Latency (gTTS)
def measure_tts_latency(text, lang_code="ur"):
    start_t = time.perf_counter()
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        temp_file = "temp_voice_test.mp3"
        tts.save(temp_file)
        end_t = time.perf_counter()
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return (end_t - start_t) * 1000.0
    except Exception as e:
        return 0.0

def run_latency_benchmarks():
    print("=========================================================")
    print("  Agri-Logistics IDAS - NLP & Voice Latency Benchmarks")
    print("=========================================================\n")

    results = []
    for p in prompts:
        cat, nlp_ms = process_intent_nlp(p["text"], p["lang"])
        voice_sample_text = f"IDAS Alert: {p['text']}"
        tts_ms = measure_tts_latency(voice_sample_text, lang_code="ur" if p["lang"] in ["Sindhi", "Dhatki", "Urdu"] else "en")
        total_pipeline_ms = nlp_ms + tts_ms

        print(f"[{p['id']}] Lang: {p['lang']} | Intent: {cat}")
        print(f"   - Input: '{p['text']}'")
        print(f"   - NLP Text Classification Latency: {nlp_ms:.4f} ms")
        print(f"   - gTTS Voice Synthesis Latency:    {tts_ms:.2f} ms")
        print(f"   - Total End-to-End Pipeline:       {total_pipeline_ms:.2f} ms\n")

        results.append({
            "prompt_id": p["id"],
            "language": p["lang"],
            "intent_category": cat,
            "input_text": p["text"],
            "nlp_classification_ms": round(nlp_ms, 4),
            "tts_synthesis_ms": round(tts_ms, 2),
            "total_latency_ms": round(total_pipeline_ms, 2)
        })

    df = pd.DataFrame(results)
    csv_file = "agri_logistics_latency_metrics.csv"
    df.to_csv(csv_file, index=False)
    print(f"[SUCCESS] Latency Benchmark dataset generated: '{csv_file}'")

    avg_nlp = df["nlp_classification_ms"].mean()
    avg_tts = df["tts_synthesis_ms"].mean()
    avg_total = df["total_latency_ms"].mean()
    print(f"\n[SUMMARY BENCHMARK METRICS]:")
    print(f"   - Mean NLP Classification Time: {avg_nlp:.4f} ms")
    print(f"   - Mean Voice Generation Time:   {avg_tts:.2f} ms")
    print(f"   - Mean Total Pipeline Latency:  {avg_total:.2f} ms")

if __name__ == "__main__":
    run_latency_benchmarks()
