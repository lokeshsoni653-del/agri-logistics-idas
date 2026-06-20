# 🌾 Agri-Logistics IDAS: Intelligent Driver Assistance System

## Overview
This repository contains the Phase 1 prototype of the **Agri-Logistics IDAS**, an AI-driven supply chain optimizer designed specifically for the agricultural corridors of Sindh, Pakistan. This project aims to bridge the digital literacy gap among rural transport drivers while optimizing true-road routing.

## Core Features
1. **True-Road GIS Routing:** Integrates OpenStreetMap (OSM) via the OSRM API to calculate accurate network distances (avoiding Euclidean straight-line flaws).
2. **Context-Aware Voice Advisory:** Triggers safety protocols based on real-time parameters (e.g., applying delicate driving thresholds when `Cargo = Fragile / Tomatoes`).
3. **Multilingual NLP Audio:** Utilizes `gTTS` to generate native-language audio cues (Sindhi, Urdu, and Dhatki), ensuring zero-literacy barriers for end-users.

## Technical Architecture
* **Frontend:** Streamlit (Stateful Python Web Framework)
* **Map Rendering:** Folium & Streamlit-Folium
* **Routing Engine:** Python `requests` targeting OSRM
* **Audio Synthesis:** `gTTS` with in-memory `io.BytesIO` buffer processing

## Academic Context
This prototype is being developed as part of a final-year Software Engineering research initiative at Sindh Agriculture University, focusing on sustainable ICT4D (Information and Communication Technology for Development) solutions.
