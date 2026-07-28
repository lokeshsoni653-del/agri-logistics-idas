import re

html = open('index.html', encoding='utf-8').read()

new_replies = '''    // Comprehensive Multilingual Intent Dictionary
    const autoReplies = {
        "hello": {
            "English": "👋 IDAS DISPATCH: Welcome TRK-119! Connected to IDAS Network. How can dispatch assist your transit today?",
            "Sindhi":  "👋 IDAS DISPATCH: Khush aayo TRK-119! IDAS Network saan jura ahyo. Kihn madad kayo?",
            "Urdu":    "👋 IDAS DISPATCH: Khush aamdeed TRK-119! IDAS Network se jur gaye hain. Kaise madad karein?",
            "Dhatki":  "👋 IDAS DISPATCH: Aavkaari TRK-119! IDAS Network saan jura aahin. Kihn madad karo?"
        },
        "route": {
            "English": "🗺️ ROUTE DISPATCH: Active corridor is Mithi → Hyderabad (162.5 km) via National Highway 8. Current position: ~56.9 km covered near Digri.",
            "Sindhi":  "🗺️ RASTO DISPATCH: Tuhajo rasto Mithi → Hyderabad (162.5 km) National Highway 8 te ahe. Digri wath 56.9 km puras thia ahe.",
            "Urdu":    "🗺️ RASTA DISPATCH: Aap ka rasta Mithi → Hyderabad (162.5 km) National Highway 8 par hai. Digri ke paas 56.9 km mukammal ho gaye hain.",
            "Dhatki":  "🗺️ RAAH DISPATCH: Taaro raah Mithi → Hyderabad (162.5 km) National Highway 8 te hai. Digri paas 56.9 km pura thia aahin."
        },
        "turn": {
            "English": "🧭 DIRECTION ADVISORY: Turn left at the upcoming junction onto National Highway 8. Follow the green route line on your navigation map.",
            "Sindhi":  "🧭 DIRECTION ADVISORY: Agte junction te khabbe moro National Highway 8 te. Map te green line rasto halo.",
            "Urdu":    "🧭 DIRECTION ADVISORY: Aage junction par baayein muren National Highway 8 par. Map par sabz line par chalein.",
            "Dhatki":  "🧭 DIRECTION ADVISORY: Aagya junction te khabey phir National Highway 8 te. Map te green line te vanj."
        },
        "speed": {
            "English": "⚡ SPEED ADVISORY: Current recommended speed is 42 km/h (Limit: 50 km/h) due to rain and night driving conditions.",
            "Sindhi":  "⚡ RAFTAR ADVISORY: Barish aur raat ji wajah saan recommended raftar 42 km/h ahe. Tezi na kayo.",
            "Urdu":    "⚡ RAFTAR ADVISORY: Baarish aur raat ki wajah se tajweez karda raftaar 42 km/h hai. Tez na chalein.",
            "Dhatki":  "⚡ RAFTAR ADVISORY: Barish ayi raat ri wajah saan recommended raftar 42 km/h hai."
        },
        "eta": {
            "English": "⏱️ ETA DISPATCH: Estimated time remaining to Hyderabad is ~2 hours 10 minutes (105.6 km remaining).",
            "Sindhi":  "⏱️ ETA DISPATCH: Hyderabad pohchan mein lagbhag 2 kalak 10 minute baaki aahin (105.6 km baaki).",
            "Urdu":    "⏱️ ETA DISPATCH: Hyderabad pahunche mein taqreeban 2 ghante 10 minute baaqi hain (105.6 km baaqi).",
            "Dhatki":  "⏱️ ETA DISPATCH: Hyderabad ppohche mein lagbhag 2 kalak 10 minute baaki aahin."
        },
        "cargo": {
            "English": "🍅 CARGO ADVISORY: Fragile Tomato load detected. Temperature: 19.2°C. Avoid harsh braking or sudden maneuvers.",
            "Sindhi":  "🍅 MAAL ADVISORY: Tamatar nazuk maal ahe. Temperature: 19.2°C. Achanak brake na kayo.",
            "Urdu":    "🍅 MAAL ADVISORY: Tamatar nazuk maal hai. Temperature: 19.2°C. Achanak brake mat lagayein.",
            "Dhatki":  "🍅 MAAL ADVISORY: Tamatar nazuk maal hai. Temperature: 19.2°C. Achanak brake na karo."
        },
        "weather": {
            "English": "🌧️ WEATHER ALERT: Rain reported on Mithi-Hyderabad highway segment. Road friction μ = 0.38 (Slippery). Keep hazard lights ON.",
            "Sindhi":  "🌧️ MOSAM ALERT: Raste te barish ahe. Sadak chikani ahe (μ = 0.38). Hazard lights chalao.",
            "Urdu":    "🌧️ MAUSAM ALERT: Raaste par baarish hai. Sadak phislan wali hai (μ = 0.38). Hazard lights chalu rakhein.",
            "Dhatki":  "🌧️ MOSAM ALERT: Raah te barish hai. Sadak chikani hai. Hazard lights chalao."
        },
        "hazard": {
            "English": "🚨 HIGH-PRIORITY ALERT: Hazard logged for TRK-119. Alternate routing via Diplo calculated. Dispatch monitoring.",
            "Sindhi":  "🚨 HIGH-PRIORITY ALERT: TRK-119 khatro register thia ahe. Diplo rasto nayo alert tayar ahe.",
            "Urdu":    "🚨 HIGH-PRIORITY ALERT: TRK-119 khatra register ho gaya hai. Diplo se naya rasta tayyar hai.",
            "Dhatki":  "🚨 HIGH-PRIORITY ALERT: TRK-119 khatro register thia hai. Diplo raah nayo alert tayar hai."
        },
        "default": {
            "English": "📡 DISPATCH ASSISTANT: Message logged for TRK-119. Active route: Mithi → Hyderabad (35% complete). Vehicle speed: 42 km/h. Dispatch is monitoring your safety.",
            "Sindhi":  "📡 DISPATCH ASSISTANT: TRK-119 paighaam record thia. Rasto: Mithi → Hyderabad (35% mukammal). Raftar: 42 km/h. Corporate tuhaji safety nigrani karay ahe.",
            "Urdu":    "📡 DISPATCH ASSISTANT: TRK-119 paigham record ho gaya. Rasta: Mithi → Hyderabad (35% mukammal). Raftar: 42 km/h. Corporate aap ki safety nigrani kar raha hai.",
            "Dhatki":  "📡 DISPATCH ASSISTANT: TRK-119 sandesh record thia. Raah: Mithi → Hyderabad (35% mukammal). Raftar: 42 km/h. Corporate taari safety nigrani kare ahe."
        }
    };'''

new_send = '''    function sendDrvMessage(e) {
        e.preventDefault();
        const inp = document.getElementById('drv-chat-input');
        const val = inp.value.trim();
        if (!val) return;

        const lowVal = val.toLowerCase();
        let cat = 'default';

        if (/route|rasto|raah|give|where|path|map|destination|way/i.test(lowVal)) {
            cat = 'route';
        } else if (/mura|muri|mor|side|direction|kahan|kayi|turn|left|right|wanjo|vanjo/i.test(lowVal)) {
            cat = 'turn';
        } else if (/speed|fast|slow|raftar|tez|limit/i.test(lowVal)) {
            cat = 'speed';
        } else if (/time|eta|distance|km|duration|pohchan|wqt|ghante|when/i.test(lowVal)) {
            cat = 'eta';
        } else if (/maal|tamatar|cargo|load|gadi|tomato|produce/i.test(lowVal)) {
            cat = 'cargo';
        } else if (/weather|rain|barish|mosam|night|raat|dark/i.test(lowVal)) {
            cat = 'weather';
        } else if (/hello|hi|salam|aayo|kiin|kean|welcome/i.test(lowVal)) {
            cat = 'hello';
        } else if (/kharab|breakdown|help|madad|emergency|accident|jam|janwar|hazard/i.test(lowVal)) {
            cat = 'hazard';
        }

        state.messages.push({ role: 'driver', original: val, english: cat === 'hazard' ? '🚨 HAZARD REPORTED BY DRIVER' : val });
        state.messages.push({ role: 'corporate', english: autoReplies[cat].English, cat: cat });
        
        inp.value = '';
        renderChat();
    }'''

start_repl = html.find('const autoReplies = {')
end_repl = html.find('};\n\n    const safetyTexts = {') + 2
html = html[:start_repl] + new_replies + html[end_repl:]

start_send = html.find('function sendDrvMessage(e) {')
end_send = html.find('}\n\n    function updateDriverContext() {') + 1
html = html[:start_send] + new_send + html[end_send:]

open('index.html', 'w', encoding='utf-8').write(html)
print('Comprehensive NLP Engine updated in index.html! New Size:', len(html))
