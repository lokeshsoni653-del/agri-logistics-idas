import re

html = open('index.html', encoding='utf-8').read()

smart_reply_code = '''    function generateSmartReply(userText) {
        const val = userText.toLowerCase().trim();
        const lang = state.lang;
        const covered = (162.5 * state.progressPct / 100).toFixed(1);
        const remKm = (162.5 - covered).toFixed(1);
        const remMin = Math.round(200 * (100 - state.progressPct) / 100);
        const hrs = Math.floor(remMin / 60), mins = remMin % 60;
        
        let spd = "72 km/h";
        if (state.weather === 'Rain' && state.time === 'Night') spd = "42 km/h (Limit: 50)";
        else if (state.weather === 'Rain' || state.time === 'Night') spd = "58 km/h (Limit: 60)";

        // 1. Route / Path / Location Queries
        if (/route|rasto|raah|give|where|path|map|destination|way|kahan|kera|location|pos/i.test(val)) {
            return {
                "English": `🗺️ ROUTE DISPATCH: Active corridor is Mithi → Hyderabad (162.5 km) via National Highway 8. Current location: ${covered} km covered near Digri. ${remKm} km remaining.`,
                "Sindhi":  `🗺️ RASTO DISPATCH: Tuhajo rasto Mithi → Hyderabad (162.5 km) National Highway 8 te ahe. Maujuda jagah: ${covered} km Digri wath puras. ${remKm} km baaki ahe.`,
                "Urdu":    `🗺️ RASTA DISPATCH: Aap ka rasta Mithi → Hyderabad (162.5 km) National Highway 8 par hai. Maujuda maqam: ${covered} km Digri ke paas. ${remKm} km baaqi hain.`,
                "Dhatki":  `🗺️ RAAH DISPATCH: Taaro raah Mithi → Hyderabad (162.5 km) National Highway 8 te hai. Maujuda thikano: ${covered} km Digri paas. ${remKm} km baaki aahin.`
            };
        }

        // 2. Turn / Direction Queries
        if (/mura|muri|mor|side|direction|kayi|turn|left|right|wanjo|vanjo|khabbe|saje/i.test(val)) {
            return {
                "English": `🧭 DIRECTION ADVISORY: Turn left at the upcoming junction onto National Highway 8. Follow the green route line on your navigation map.`,
                "Sindhi":  `🧭 DIRECTION ADVISORY: Agte junction te khabbe moro National Highway 8 te. Map te green line rasto halo.`,
                "Urdu":    `🧭 DIRECTION ADVISORY: Aage junction par baayein muren National Highway 8 par. Map par sabz line par chalein.`,
                "Dhatki":  `🧭 DIRECTION ADVISORY: Aagya junction te khabey phir National Highway 8 te. Map te green line te vanj.`
            };
        }

        // 3. Speed / Raftar Queries
        if (/speed|fast|slow|raftar|tez|limit|chalo/i.test(val)) {
            return {
                "English": `⚡ SPEED ADVISORY: Current recommended speed is ${spd} due to ${state.weather} weather and ${state.time} conditions. Maintain safe braking distance.`,
                "Sindhi":  `⚡ RAFTAR ADVISORY: Recommended raftar ${spd} ahe (${state.weather} weather, ${state.time}). Tezi na kayo, safe doori rakho.`,
                "Urdu":    `⚡ RAFTAR ADVISORY: Tajweez karda raftaar ${spd} hai (${state.weather} mausam, ${state.time}). Tez na chalein, mehfooz fasla rakhein.`,
                "Dhatki":  `⚡ RAFTAR ADVISORY: Recommended raftar ${spd} hai (${state.weather} weather, ${state.time}). Tezi na karo.`
            };
        }

        // 4. Time / ETA / Distance Queries
        if (/time|eta|distance|km|duration|pohchan|wqt|ghante|when|reach/i.test(val)) {
            return {
                "English": `⏱️ ETA DISPATCH: Estimated time remaining to Hyderabad is ~${hrs}h ${mins}m (${remKm} km remaining). Drive safely!`,
                "Sindhi":  `⏱️ ETA DISPATCH: Hyderabad pohchan mein lagbhag ${hrs} kalak ${mins} minute baaki aahin (${remKm} km baaki). Salaamti halo!`,
                "Urdu":    `⏱️ ETA DISPATCH: Hyderabad pahunche mein taqreeban ${hrs} ghante ${mins} minute baaqi hain (${remKm} km baaqi). Salamti se chalein!`,
                "Dhatki":  `⏱️ ETA DISPATCH: Hyderabad ppohche mein lagbhag ${hrs} kalak ${mins} minute baaki aahin (${remKm} km baaki). Salaamti vanj!`
            };
        }

        // 5. Cargo / Tomatoes / Load Queries
        if (/maal|tamatar|cargo|load|gadi|tomato|produce|fragile/i.test(val)) {
            return {
                "English": `🍅 CARGO ADVISORY: Active cargo: ${state.cargo}. Temperature: 19.2°C (Refrigerated). Avoid harsh braking or sudden maneuvers.`,
                "Sindhi":  `🍅 MAAL ADVISORY: Gadi mein ${state.cargo} maal ahe. Temp: 19.2°C. Achanak brake na kayo.`,
                "Urdu":    `🍅 MAAL ADVISORY: Gadi mein ${state.cargo} maal hai. Temp: 19.2°C. Achanak brake mat lagayein.`,
                "Dhatki":  `🍅 MAAL ADVISORY: Gadi mein ${state.cargo} maal hai. Temp: 19.2°C. Achanak brake na karo.`
            };
        }

        // 6. Weather / Rain / Night Queries
        if (/weather|rain|barish|mosam|night|raat|dark|slippery/i.test(val)) {
            return {
                "English": `🌧️ WEATHER ALERT: Current weather: ${state.weather} (${state.time}). Road friction μ = 0.38 (Wet). Keep hazard lights ON and reduce speed.`,
                "Sindhi":  `🌧️ MOSAM ALERT: Maujuda mosam: ${state.weather} (${state.time}). Sadak chikani ahe. Hazard lights chalao.`,
                "Urdu":    `🌧️ MAUSAM ALERT: Maujuda mausam: ${state.weather} (${state.time}). Sadak phislan wali hai. Hazard lights chalu rakhein.`,
                "Dhatki":  `🌧️ MOSAM ALERT: Maujuda mosam: ${state.weather} (${state.time}). Sadak chikani hai. Hazard lights chalao.`
            };
        }

        // 7. Greetings
        if (/hello|hi|salam|aayo|kiin|kean|welcome|khush/i.test(val)) {
            return {
                "English": `👋 IDAS DISPATCH: Hello TRK-119! Connected to IDAS Network on Mithi → Hyderabad route (${state.progressPct}% complete). How can dispatch assist?`,
                "Sindhi":  `👋 IDAS DISPATCH: Khush aayo TRK-119! Mithi → Hyderabad rasto (${state.progressPct}% mukammal). Kihn madad kayo?`,
                "Urdu":    `👋 IDAS DISPATCH: Khush aamdeed TRK-119! Mithi → Hyderabad rasta (${state.progressPct}% mukammal). Kaise madad karein?`,
                "Dhatki":  `👋 IDAS DISPATCH: Aavkaari TRK-119! Mithi → Hyderabad raah (${state.progressPct}% mukammal). Kihn madad karo?`
            };
        }

        // 8. Hazard / Emergency
        if (/kharab|breakdown|help|madad|emergency|accident|jam|janwar|hazard|khatro/i.test(val)) {
            return {
                "English": `🚨 HIGH-PRIORITY ALERT: Hazard logged for TRK-119 near ${covered} km. Alternate routing via Diplo calculated. Dispatch monitoring.`,
                "Sindhi":  `🚨 HIGH-PRIORITY ALERT: TRK-119 ${covered} km wath khatro register thia. Diplo rasto nayo alert tayar ahe.`,
                "Urdu":    `🚨 HIGH-PRIORITY ALERT: TRK-119 ${covered} km ke paas khatra register ho gaya. Diplo se naya rasta tayyar hai.`,
                "Dhatki":  `🚨 HIGH-PRIORITY ALERT: TRK-119 ${covered} km paas khatro register thia. Diplo raah nayo alert tayar hai.`
            };
        }

        // 9. Intelligent Dynamic Context Fallback
        return {
            "English": `📡 DISPATCH ASSISTANT: Message logged for TRK-119. Active route: Mithi → Hyderabad (${state.progressPct}% complete, ${covered} km). Speed: ${spd}. Dispatch monitoring safety.`,
            "Sindhi":  `📡 DISPATCH ASSISTANT: TRK-119 paighaam record thia. Rasto: Mithi → Hyderabad (${state.progressPct}% mukammal, ${covered} km). Raftar: ${spd}. Corporate tuhaji safety nigrani karay ahe.`,
            "Urdu":    `📡 DISPATCH ASSISTANT: TRK-119 paigham record ho gaya. Rasta: Mithi → Hyderabad (${state.progressPct}% mukammal, ${covered} km). Raftar: ${spd}. Corporate aap ki safety nigrani kar raha hai.`,
            "Dhatki":  `📡 DISPATCH ASSISTANT: TRK-119 sandesh record thia. Raah: Mithi → Hyderabad (${state.progressPct}% mukammal, ${covered} km). Raftar: ${spd}. Corporate taari safety nigrani kare ahe.`
        };
    }'''

new_render = '''    function renderChat() {
        const boxCorp = document.getElementById('corp-chat-box');
        const boxDrv  = document.getElementById('drv-chat-box');
        
        let htmlCorp = '', htmlDrv = '';
        state.messages.forEach(msg => {
            const isDrv = msg.role === 'driver';
            const textDrv = isDrv ? msg.original : (msg.replyObj ? msg.replyObj[state.lang] : msg.english);
            
            htmlCorp += `
                <div class="chat-row ${isDrv ? 'driver' : 'corporate'}">
                    <div class="chat-avatar">${isDrv ? '🚚' : '🏢'}</div>
                    <div>
                        <div class="chat-bubble">${msg.english}</div>
                        <div class="chat-meta">${isDrv ? '🌐 ' + state.lang + ' → EN' : '🏢 Corporate'}</div>
                    </div>
                </div>`;
            
            htmlDrv += `
                <div class="chat-row ${isDrv ? 'driver' : 'corporate'}">
                    <div class="chat-avatar">${isDrv ? '🚚' : '🏢'}</div>
                    <div>
                        <div class="chat-bubble">${textDrv}</div>
                        <div class="chat-meta">${isDrv ? 'You (' + state.lang + ')' : '🏢 → ' + state.lang}</div>
                    </div>
                </div>`;
        });

        boxCorp.innerHTML = htmlCorp;
        boxDrv.innerHTML  = htmlDrv;
        boxCorp.scrollTop = boxCorp.scrollHeight;
        boxDrv.scrollTop  = boxDrv.scrollHeight;
    }'''

new_send_drv = '''    function sendDrvMessage(e) {
        e.preventDefault();
        const inp = document.getElementById('drv-chat-input');
        const val = inp.value.trim();
        if (!val) return;

        const smartReply = generateSmartReply(val);
        const isHazard = /kharab|breakdown|help|madad|emergency|accident|jam|janwar|hazard|khatro/i.test(val);
        
        state.messages.push({ role: 'driver', original: val, english: isHazard ? '🚨 HAZARD REPORTED BY DRIVER: ' + val : val });
        state.messages.push({ role: 'corporate', english: smartReply.English, replyObj: smartReply });
        
        inp.value = '';
        renderChat();
    }'''

# Replace autoReplies block with generateSmartReply
start_repl = html.find('const autoReplies = {')
end_repl = html.find('};\n\n    const safetyTexts = {') + 2
html = html[:start_repl] + smart_reply_code + html[end_repl:]

# Replace renderChat block
start_rend = html.find('function renderChat() {')
end_rend = html.find('}\n\n    function sendCorpMessage(e) {') + 1
html = html[:start_rend] + new_render + html[end_rend:]

# Replace sendDrvMessage block
start_send = html.find('function sendDrvMessage(e) {')
end_send = html.find('}\n\n    function updateDriverContext() {') + 1
html = html[:start_send] + new_send_drv + html[end_send:]

open('index.html', 'w', encoding='utf-8').write(html)
print('Hyper-Accurate Dynamic AI Engine injected into index.html! New Size:', len(html))
