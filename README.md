# Agri-Logistics IDAS — Intelligent Driver Assistance System

> **Context-Aware Safety Telematics & Trilingual Vernacular Voice Guidance for Agricultural Supply Chains in Rural Sindh**  
> **Live Production Portal**: [https://agri-idas.tech](https://agri-idas.tech)

[![IEEE Karachi Section](https://img.shields.io/badge/IEEE-Karachi%20Section-00629B?style=for-the-badge&logo=ieee&logoColor=white)](https://ieee.org)
[![EPICS in IEEE](https://img.shields.io/badge/Grant%20Proposal-EPICS%20in%20IEEE%20($10k)-FF6F00?style=for-the-badge)](https://epics.ieee.org)
[![Community Partner](https://img.shields.io/badge/NPO%20Partner-SPO%20Pakistan-2E7D32?style=for-the-badge)](https://spopk.org)
[![Academic Supervisor](https://img.shields.io/badge/Supervisor-Prof.%20Dr.%20B.S.%20Chowdhry-8E24AA?style=for-the-badge)](https://bschowdhry.info)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/UI%20Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

---

## 📄 Academic Attribution & Leadership

* **Principal Student Investigator & Lead Architect**: **Lokesh Kumar**  
  *Student Member, IEEE* (Member # `99402233`, Karachi Section) · Student ID: `2k22-SE-42`  
  *Department of Software Engineering, Sindh Agriculture University (SAU), Tandojam, Pakistan*  
  *Email*: [2K22-SE-42@student.sau.edu.pk](mailto:2K22-SE-42@student.sau.edu.pk) | [lokeshsoni653@gmail.com](mailto:lokeshsoni653@gmail.com)
* **Academic Supervisor & Senior Investigator**: **Prof. Dr. Bhawani Shankar Chowdhry**  
  *Sitara-i-Imtiaz*, *Izaz-e-Fazeelat*  
  *HEC Distinguished National Professor & Professor Emeritus, Mehran University of Engineering and Technology (MUET)*  
  *Former Dean, FECCE & Life Senior Member, IEEE*
* **IEEE Section & Technical Publishing Advisor**: **Engr. Parkash Lohana**  
  *Director CSPD, MAJU · Publication Chair & Conference Secretary, IEEE KHI-HTC*
* **Institutional Community Partner**: **Strengthening Participatory Organisation (SPO)**  
  *Regional Office, Hyderabad, Sindh, Pakistan*  
  *Program Lead*: **Shewa Ram Suthar** (*Program Manager, Sindh*)

---

## 🌾 Abstract & Problem Formulation

Agricultural transit across Lower Sindh—predominantly the **Mithi $\rightarrow$ Mirpurkhas $\rightarrow$ Hyderabad** transit corridor—experiences catastrophic post-harvest crop losses (**exceeding 30% for perishable produce like tomatoes and mangoes**) alongside unbudgeted diesel deficits. Field evaluations reveal three core systemic bottlenecks:

1. **The Digital & Text-Literacy Barrier:** Standard commercial telematics and GPS navigation engines (Google Maps, Waze) rely on English or Urdu textual UI, alienating rural commercial transport operators.
2. **Vernacular Linguistic Heterogeneity:** Drivers predominantly operate in indigenous regional dialects (**Sindhi**, **Dhatki**, and regional vernacular Urdu).
3. **Dynamic Environmental Road Hazards:** Night driving, severe monsoon flash-flooding, submerged bridges, and unpaved arterial rural routes dramatically increase rollover accidents and perishable cargo bruising.

**Agri-Logistics IDAS** resolves these challenges by coupling an **OSRM True-Road GIS Engine**, a **Bidirectional Trilingual NLP Translation Layer**, an automated **4-Tier Context-Aware Safety Rules Matrix**, and a **Sub-Second Multilingual Voice Advisory Engine** into a zero-literacy mobile cockpit.

---

## 🏗️ End-to-End System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          Agri-Logistics IDAS System Architecture                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [1. USER INTERACTION & COCKPIT LAYER]                                                 │
│       ├── Corporate Dispatch Console (English Management View)                         │
│       └── Driver Navigation HUD (Trilingual Vernacular Interface: Sindhi/Urdu/Dhatki)  │
│                                      │                                                 │
│                                      ▼                                                 │
│  [2. BIDIRECTIONAL NLP TRANSLATION & HAZARD DETECTION ENGINE]                          │
│       ├── Driver Dialect Normalizer (Romanized Sindhi / Dhatki / Urdu)                 │
│       ├── Lexical Hazard Parser (Flooded Causeways, Blocked Roads, Weather Warnings)   │
│       └── Corporate English Command Synthesizer                                        │
│                                      │                                                 │
│                                      ▼                                                 │
│  [3. GEOSPATIAL ROUTING & TELEMETRICS LAYER]                                           │
│       ├── Open Source Routing Machine (OSRM) Engine                                    │
│       ├── Real-Time Turn-by-Turn Instruction Parser                                    │
│       └── Dynamic Folium Geospatial Map Engine with Outage Fallback Mechanism          │
│                                      │                                                 │
│                                      ▼                                                 │
│  [4. CONTEXT-AWARE SAFETY & SPEECH ADVISORY PIPELINE]                                  │
│       ├── 4-Tier Risk Inference Matrix (Normal → Advisory → Critical → Extreme)        │
│       ├── Fragile Cargo Decay Suffix Synthesizer ("Nazuk maal aahay, ahista halo")     │
│       └── Cached gTTS Audio Synthesis Layer (@st.cache_data for Sub-Second Playback)   │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
---

## 💻 Local Installation & Reproducibility Guide

### Prerequisites
* Python `3.10` or `3.11`
* Git

```bash
# 1. Clone the repository
git clone https://github.com/lokeshsoni653-del/agri-logistics-idas.git
cd agri-logistics-idas

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Launch the IDAS platform
streamlit run agri_logistics_idas.py
```

---

## 📚 Formal Academic Citation

If you utilize this architecture, dataset parameters, or dialectal NLP dictionaries in your research, cite this work as follows:

```bibtex
@article{kumar2026idas,
  author    = {Kumar, Lokesh and Lohana, Parkash and Suthar, Shewa Ram and Chowdhry, Bhawani Shankar},
  title     = {Agri-Logistics IDAS: A Trilingual, Context-Aware Intelligent Driver Assistance System for Zero-Literacy Rural Agricultural Supply Chains in Sindh},
  journal   = {Technical Report - IEEE Karachi Section & Sindh Agriculture University},
  year      = {2026},
  url       = {https://agri-idas.tech},
  note      = {Supported by EPICS in IEEE Grant Proposal & Strengthening Participatory Organisation (SPO)}
}
```

---

## 📜 Licensing
Distributed under the **MIT License**. Maintained by **Lokesh Kumar** under the academic guidance of **Prof. Dr. B.S. Chowdhry**.
