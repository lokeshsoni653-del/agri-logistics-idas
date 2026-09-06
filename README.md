# Agri-Logistics IDAS — Intelligent Driver Assistance System

> **Production-Grade Research Prototype — Phase 3 (Context-Aware Safety)**  
> **Live System Portal**: [https://agri-idas.tech](https://agri-idas.tech)

---

## 📄 Research Context & Citation

* **Research Paper Title**: *"Bridging the Digital Literacy Gap in Rural Agri-Logistics: A Trilingual, Context-Aware Intelligent Driver Assistance System for the Sindh Agricultural Supply Chain"*
* **Author**: Lokesh Kumar, *Student Member, IEEE* (Member # `99402233`, Karachi Section · Student ID: `2k22-SE-42`)
* **Email**: [2K22-SE-42@student.sau.edu.pk](mailto:2K22-SE-42@student.sau.edu.pk)
* **Institution**: Department of Software Engineering, Sindh Agriculture University, Tandojam, Pakistan
* **Supervision & Academic Guidance**: Prof. Dr. Bhawani Shankar Chowdhry (IEEE Life Senior Member / Distinguished National Professor)

---

## 🌾 Abstract & Research Problem

Agricultural logistics across rural Sindh (particularly the **Mithi $\rightarrow$ Hyderabad** transit corridor) suffer high post-harvest crop losses ($\sim 35-40\%$ for delicate produce like tomatoes) due to:
1. **Digital Literacy Barriers**: Traditional GPS & fleet management applications assume English/Urdu text literacy.
2. **Language Heterogeneity**: Rural truck drivers predominantly communicate in regional dialects (**Sindhi**, **Urdu**, and **Dhatki**).
3. **Dynamic Environmental Hazards**: Night driving, heavy monsoon rainfall, flooding, and unlit rural road hazards drastically increase accident risk and cargo spoilage.

The **Agri-Logistics IDAS** addresses this gap by combining **Trilingual NLP Translation**, **OSRM True-Road Routing**, **Context-Aware Multi-Tier Safety Alerting**, and **gTTS Multilingual Audio Advisories** into a zero-literacy-barrier mobile interface.

---

## 🏗️ System Architecture

The architecture consists of four decoupled processing layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Agri-Logistics IDAS Pipeline                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [1. Driver / Corporate Interface]                                      │
│      ├── Mobile-Responsive Dispatch Chat                                │
│      └── Context Simulator Controls (Cargo, Weather, Time)             │
│                                                                         │
│  [2. Trilingual NLP Engine]                                             │
│      ├── Bidirectional NLP (Sindhi / Urdu / Dhatki ↔ Corporate English) │
│      └── Regional Hazard Keyword & Emergency Detector                   │
│                                                                         │
│  [3. OSRM True-Road Routing Layer]                                      │
│      ├── OpenStreetMap True-Road Polyline Geometry                      │
│      └── Off-Grid Network Fallback Map Renderer                         │
│                                                                         │
│  [4. Context-Aware Safety & Audio Layer]                                │
│      ├── 4-Tier Risk Matrix (Extreme, Critical, Warning, Standard)      │
│      └── gTTS Multilingual Voice Engine (@st.cache_data)                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Features

1. **Trilingual Dispatch Chat (Sindhi, Urdu, Dhatki)**:
   - Real-time bidirectional chat matching driver hazard inputs against regional phrasebooks.
   - Instant corporate auto-reply bot responding directly in the driver's chosen dialect.
   - Mobile-optimized layout with zero text wrapping on action buttons.

2. **4-Tier Context-Aware Safety Matrix**:
   - **Tier 4: EXTREME RISK** (Night + Rain + Fragile Cargo) — Pulsing high-priority safety alert.
   - **Tier 3: CRITICAL RISK** (Wet Roads + Fragile Cargo) — Braking distance & crop bruising advisory.
   - **Tier 2: WARNING** (Night Driving / Wet Roads / Fragile Cargo).
   - **Tier 1: STANDARD** (Clear driving conditions).

3. **True-Road OSRM Navigation**:
   - Interactive Folium polyline route calculation from Mithi to Hyderabad via Naukot & Tando Ghulam Ali.
   - Pure HTML map injection eliminating Streamlit component key conflicts.

4. **gTTS Multilingual Audio Guidance**:
   - Spoken maneuver advisories in Romanized Sindhi, Urdu, and Dhatki.
   - Preposition-cleaned natural pronunciation and `@st.cache_data` latency optimization.

5. **Live Route Progress & Demo Simulator**:
   - Progress bar tracking distance covered (`km`) and dynamic ETA countdown (`hours/mins`).
   - Interactive demo slider to simulate route progression during research evaluation.

---

## 📁 Repository Structure

```text
agri-idas/
├── agri_logistics_idas.py    # Main Streamlit Phase 3 Application & UI
├── routing.py                 # OSRM True-Road Engine & Map Renderers
├── voice_advisory.py          # gTTS Trilingual Audio Advisory Module
├── requirements.txt           # Python Dependencies
├── task.md                    # System Task Tracker & Audit Log
└── README.md                  # Comprehensive Academic Documentation
```

---

## 💻 Local Setup & Execution

1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-username/agri-idas.git
   cd agri-idas
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   streamlit run agri_logistics_idas.py
   ```

4. **Access Portal**:
   Open browser at `http://localhost:8501` or visit the live deployment at [https://agri-idas.tech](https://agri-idas.tech).

---

## 📜 IEEE Citation Format

```bibtex
@inproceedings{kumar2024agri,
  author    = {Kumar, Lokesh},
  title     = {Bridging the Digital Literacy Gap in Rural Agri-Logistics: A Trilingual, Context-Aware Intelligent Driver Assistance System for the Sindh Agricultural Supply Chain},
  booktitle = {Proceedings of the Sindh Agriculture University Research Symposium},
  address   = {Tandojam, Pakistan},
  year      = {2024},
  note      = {Supervision & Guidance: Prof. Dr. Bhawani Shankar Chowdhry}
}
```

---

*© 2024 Lokesh Kumar · Department of Software Engineering · Sindh Agriculture University, Tandojam.*
