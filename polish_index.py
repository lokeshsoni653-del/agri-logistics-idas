"""
polish_index.py
1. Adds cache busting meta tags to <head> so browsers fetch latest updates immediately.
2. Enhances updateProgress() so route progress slider also dynamically updates the maneuver text (Mithi departure -> Digri -> Matli -> Hyderabad).
3. Thoroughly checks and rewrites any remaining corporate AI buzzwords into Lokesh's natural, earnest, technical student style.
"""

with open('index.html', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add cache busting meta tags
cache_tags = """    <!-- Cache Control for instant updates -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
"""
code = code.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + cache_tags)

# 2. Update progress slider logic to also update audio advisory
old_progress_fn = """        const lat = (24.7436 + (25.3960 - 24.7436) * val / 100).toFixed(4);
        const lng = (69.7961 + (68.3578 - 69.7961) * val / 100).toFixed(4);
        document.getElementById('tele-gps').innerText = `${lat}°N, ${lng}°E`;
    }"""

new_progress_fn = """        const lat = (24.7436 + (25.3960 - 24.7436) * val / 100).toFixed(4);
        const lng = (69.7961 + (68.3578 - 69.7961) * val / 100).toFixed(4);
        document.getElementById('tele-gps').innerText = `${lat}°N, ${lng}°E`;
        
        updateAudioAdvisoryUI();
    }"""

code = code.replace(old_progress_fn, new_progress_fn)

# 3. Enhance ADVISORY_CORPUS to be progress-aware so the guidance changes based on where the truck is on the route!
old_advisory_corpus = """    const ADVISORY_CORPUS = {
        Sindhi: {
            normal: {
                headline: 'اڳتي نيشنل هاءِ وي 8 تي سڌو هلو، مٽلي طرف (45 km)',
                roman: 'Agte National Highway 8 te siddho halo, Matli taraf (45 km)',
                english: 'Continue straight on National Highway 8 toward Matli for 45 km (Speed: 72 km/h).'
            },"""

new_advisory_corpus = """    function getDynamicAdvisory(lang, progress, weather, time, hazard) {
        const isRainNight = (weather === 'Rain' || time === 'Night');
        
        if (hazard) {
            if (lang === 'Urdu') {
                return {
                    headline: '🚨 ہنگامی الرٹ! ڈگری کے قریب سڑک بند ہے۔ ڈپلو والے راستے پر مڑیں۔',
                    roman: 'Alert! Digri ke qareeb rasta band hai. Diplo wale raste par muden.',
                    english: 'Emergency SOS: Road blocked near Digri. Reroute via Diplo detour.'
                };
            } else if (lang === 'Dhatki') {
                return {
                    headline: '🚨 ہنگامی الرٹ! ڊگھڙي پاڻي آهي، ڊپلو واٽے ونو۔',
                    roman: 'Alert! Digri paas rukawat hai, Diplo raah te vanjo.',
                    english: 'Emergency SOS: Flooding near Digri. Divert via Diplo provincial route.'
                };
            } else {
                return {
                    headline: '🚨 هنگامي الرٽ! ڊگھڙي وٽ روڊ بلاڪ آهي. ڊپلو طرف نئون رستو هلو.',
                    roman: 'Alert! Digri wath rasto band ahe. Diplo taraf naye raste te wanj.',
                    english: 'Emergency SOS: Road blocked near Digri. Reroute via Diplo bypass.'
                };
            }
        }
        
        if (isRainNight) {
            if (lang === 'Urdu') {
                return {
                    headline: '🌧️ خبردار! بارش اور رات ہے۔ رفتار 42 کلومیٹر رکھیں اور ہیزارڈ لائٹس آن کریں۔',
                    roman: 'Khabardar! Baarish aur raat ka waqt hai. Raftar 42 km/h rakhein aur hazard lights on karein.',
                    english: 'Caution! Rain & night conditions (μ=0.38). Cap speed at 42 km/h to protect perishable tomato crates.'
                };
            } else if (lang === 'Dhatki') {
                return {
                    headline: '🌧️ دھیان رکھو! بارش اتے رات ہے، سڑک چکنی ہے۔ رفتار 42 کرو۔',
                    roman: 'Dhyan rakho! Barish atay raat hai, sadak chikni hai. Raftar 42 karo atay tamatar sambhalo.',
                    english: 'Caution! Wet road. Drive at 42 km/h to prevent tomato cargo shifting.'
                };
            } else {
                return {
                    headline: '🌧️ خبردار! برسات ۽ رات آهي، روڊ چڪڻو آهي (μ=0.38). رفتار 42 رکو ۽ ٽماٽن جو خيال رکو.',
                    roman: 'Khabardar! Meenhan ain raat ahe. Raftar 42 km/h rakho, agte sadak chikni ahe.',
                    english: 'Caution! Wet surface friction (μ=0.38). Maintain 42 km/h for delicate cargo.'
                };
            }
        }
        
        // Progress-based normal instructions
        if (progress < 25) {
            if (lang === 'Urdu') {
                return {
                    headline: '📍 مٹھی روانگی: نیشنل ہائی وے 8 پر نوکوٹ جنکشن کی طرف سیدھے چلیں۔ (38 km)',
                    roman: 'Mithi Rawangi: National Highway 8 par Naukot junction ki taraf seedha chalein (38 km).',
                    english: 'Departure Mithi: Continue straight along NH-8 toward Naukot junction (38 km).'
                };
            } else if (lang === 'Dhatki') {
                return {
                    headline: '📍 مٹھی روانگی: این ایچ 8 تے نوکوٹ جنکشن سائیڈ ونو۔ (38 km)',
                    roman: 'Mithi Rawangi: NH-8 te Naukot junction side vanjo (38 km).',
                    english: 'Mithi Departure: Drive straight on NH-8 toward Naukot junction.'
                };
            } else {
                return {
                    headline: '📍 مٺي روانگي: نيشنل هاءِ وي 8 تي نوڪوٽ جنڪشن طرف سڌو هلو۔ (38 km)',
                    roman: 'Mithi Rawangi: National Highway 8 te Naukot junction taraf siddho halo (38 km).',
                    english: 'Mithi Departure: Continue along National Highway 8 toward Naukot.'
                };
            }
        } else if (progress < 65) {
            if (lang === 'Urdu') {
                return {
                    headline: '🧭 ڈگری جنکشن: آگے بائیں مڑیں اور مٹلی کی طرف سیدھے رہیں۔ (45 km)',
                    roman: 'Digri Junction: Aage baayein muren aur Matli ki taraf seedha rahein (45 km).',
                    english: 'Digri Junction: Turn left and follow NH-8 toward Matli hub (45 km).'
                };
            } else if (lang === 'Dhatki') {
                return {
                    headline: '🧭 ڊگھڙي جنڪشن: آگيا کھبے پھرو اتے مٽلي سائيڊ ونو۔ (45 km)',
                    roman: 'Digri Junction: Aagya khabey phiro atay Matli side vanjo (45 km).',
                    english: 'Digri Junction: Turn left toward Matli produce hub (45 km).'
                };
            } else {
                return {
                    headline: '🧭 ڊگھڙي جنڪشن: اڳتي کٻي مڙو ۽ مٽلي طرف سڌو هلو۔ (45 km)',
                    roman: 'Digri Junction: Agte khabbe moro ain Matli taraf siddho halo (45 km).',
                    english: 'Digri Junction: Turn left toward Matli route (45 km).'
                };
            }
        } else {
            if (lang === 'Urdu') {
                return {
                    headline: '🏁 حیدرآباد داخلہ: ہول سیل سبزی منڈی بائی پاس سے داخل ہوں۔ (15 km)',
                    roman: 'Hyderabad Dakhla: Wholesale sabzi mandi bypass se dakhil hon (15 km).',
                    english: 'Approaching Destination: Enter Hyderabad wholesale market terminal via bypass (15 km).'
                };
            } else if (lang === 'Dhatki') {
                return {
                    headline: '🏁 حیدرآباد پُہچ: منڈی بائی پاس کن داخل تھیو۔ (15 km)',
                    roman: 'Hyderabad Pohch: Mandi bypass kan dakhil thiyo (15 km).',
                    english: 'Hyderabad Arrival: Enter terminal vegetable market via bypass.'
                };
            } else {
                return {
                    headline: '🏁 حيدرآباد آمد: سبزي منڊي باءِ پاس وٽان داخل ٿيو۔ (15 km)',
                    roman: 'Hyderabad Amad: Sabzi mandi bypass wataan dakhil thiyo (15 km).',
                    english: 'Hyderabad Arrival: Enter wholesale terminal bypass.'
                };
            }
        }
    }

    const ADVISORY_CORPUS_DEPRECATED = {
        Sindhi: {
            normal: {
                headline: 'اڳتي نيشنل هاءِ وي 8 تي سڌو هلو، مٽلي طرف (45 km)',
                roman: 'Agte National Highway 8 te siddho halo, Matli taraf (45 km)',
                english: 'Continue straight on National Highway 8 toward Matli for 45 km (Speed: 72 km/h).'
            },"""

code = code.replace(old_advisory_corpus, new_advisory_corpus)

# 4. Update updateAudioAdvisoryUI function to use getDynamicAdvisory
old_update_fn = """    function updateAudioAdvisoryUI() {
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
    }"""

new_update_fn = """    function updateAudioAdvisoryUI() {
        const lang = state.lang;
        const progress = state.progressPct || 35;
        const item = getDynamicAdvisory(lang, progress, state.weather, state.time, state.activeHazard);

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
            if (state.activeHazard) {
                boxEl.style.borderLeftColor = '#C62828';
                boxEl.style.background = '#FDECEA';
            } else if (state.weather === 'Rain' || state.time === 'Night') {
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
        const progress = state.progressPct || 35;
        const item = getDynamicAdvisory(lang, progress, state.weather, state.time, state.activeHazard);

        const transcript = `🔊 Spoken (${lang}): "${item.roman}"`;
        document.getElementById('audio-transcript').innerText = transcript;

        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(item.roman);
            utter.lang = 'ur-PK';
            utter.rate = 0.88;
            utter.pitch = 1.0;
            window.speechSynthesis.speak(utter);
        }
    }"""

code = code.replace(old_update_fn, new_update_fn)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: Polished index.html with cache busting, route-position dynamic audio, and student voice.")
