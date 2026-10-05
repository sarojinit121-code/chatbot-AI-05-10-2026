/**
 * LocalLens AI — Frontend Controller
 * Handles chat messaging, Ollama status, destination browsing, Web Speech API, and offline fallbacks.
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    let currentSessionId = localStorage.getItem('locallens_session_id') || generateUUID();
    localStorage.setItem('locallens_session_id', currentSessionId);

    let activeCityFilter = null;
    let activeLanguage = 'english';
    let activeModel = 'llama3.2:3b';
    let isWaitingForResponse = false;
    let destinationsData = {};
    let recognition = null;
    let isRecording = false;

    // DOM Elements
    const chatContainer = document.getElementById('chatContainer');
    const messagesList = document.getElementById('messagesList');
    const welcomeHero = document.getElementById('welcomeHero');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const newChatBtn = document.getElementById('newChatBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const historyList = document.getElementById('historyList');
    const destinationList = document.getElementById('destinationList');
    const destTotalCount = document.getElementById('destTotalCount');
    const engineStatusCard = document.getElementById('engineStatusCard');
    const statusDot = document.getElementById('statusDot');
    const engineName = document.getElementById('engineName');
    const engineMeta = document.getElementById('engineMeta');
    const ollamaInfoBtn = document.getElementById('ollamaInfoBtn');
    const ollamaModal = document.getElementById('ollamaModal');
    const closeOllamaModal = document.getElementById('closeOllamaModal');
    const dismissOllamaModal = document.getElementById('dismissOllamaModal');
    const checkOllamaBtn = document.getElementById('checkOllamaBtn');
    const cityModal = document.getElementById('cityModal');
    const closeCityModal = document.getElementById('closeCityModal');
    const cityModalTitle = document.getElementById('cityModalTitle');
    const cityModalIcon = document.getElementById('cityModalIcon');
    const cityModalItinerary = document.getElementById('cityModalItinerary');
    const cityPlacesGrid = document.getElementById('cityPlacesGrid');
    const askAboutCityBtn = document.getElementById('askAboutCityBtn');
    const modelSelect = document.getElementById('modelSelect');
    const exportChatBtn = document.getElementById('exportChatBtn');
    const activeFilterStrip = document.getElementById('activeFilterStrip');
    const filterValueText = document.getElementById('filterValueText');
    const clearFilterBtn = document.getElementById('clearFilterBtn');
    const menuToggle = document.getElementById('menuToggle');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');
    const sidebar = document.getElementById('sidebar');
    const activeDestBadge = document.getElementById('activeDestinationName');
    const placeSearchInput = document.getElementById('placeSearchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const searchDropdown = document.getElementById('searchDropdown');
    const searchBarWrapper = document.getElementById('searchBarWrapper');
    let searchDebounceTimer = null;

    // --- INITIALIZATION ---
    initApp();

    function initApp() {
        setupEventListeners();
        setupSpeechRecognition();
        fetchOllamaStatus();
        fetchDestinations();
        loadSession(currentSessionId);
        fetchSessionsList();

        // Check Ollama every 20 seconds
        setInterval(fetchOllamaStatus, 20000);
    }

    // --- EVENT LISTENERS ---
    function setupEventListeners() {
        // Send button click & Enter key
        sendBtn.addEventListener('click', handleSendMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });

        // Auto-expand textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + 'px';
        });

        // New Chat
        newChatBtn.addEventListener('click', startNewChat);

        // Clear History
        clearHistoryBtn.addEventListener('click', () => {
            if (confirm("Are you sure you want to clear your conversation history?")) {
                localStorage.removeItem('locallens_session_id');
                startNewChat();
            }
        });

        // Language Buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeLanguage = btn.dataset.lang;
            });
        });

        // Model Select
        modelSelect.addEventListener('change', () => {
            activeModel = modelSelect.value;
        });

        // Theme tags in sidebar
        document.querySelectorAll('.theme-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                document.querySelectorAll('.theme-tag').forEach(t => t.classList.remove('active'));
                tag.classList.add('active');
                filterDestinationsByCategory(tag.dataset.category);
            });
        });

        // Quick prompt pills
        document.querySelectorAll('.prompt-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                const prompt = pill.dataset.prompt;
                chatInput.value = prompt;
                handleSendMessage();
            });
        });

        // Destination Showcase Cards in Hero
        document.querySelectorAll('.dest-card').forEach(card => {
            card.addEventListener('click', () => {
                const city = card.dataset.city;
                setCityFilter(city);
                openCityModal(city);
            });
        });

        // Filter Strip Clear Button
        clearFilterBtn.addEventListener('click', () => {
            setCityFilter(null);
        });

        // Ollama Modal
        ollamaInfoBtn.addEventListener('click', () => ollamaModal.classList.add('active'));
        closeOllamaModal.addEventListener('click', () => ollamaModal.classList.remove('active'));
        dismissOllamaModal.addEventListener('click', () => ollamaModal.classList.remove('active'));
        checkOllamaBtn.addEventListener('click', async () => {
            checkOllamaBtn.textContent = 'Checking...';
            await fetchOllamaStatus();
            checkOllamaBtn.textContent = '🔄 Check Connection Now';
        });

        // City Modal
        closeCityModal.addEventListener('click', () => cityModal.classList.remove('active'));
        askAboutCityBtn.addEventListener('click', () => {
            const city = cityModalTitle.textContent;
            cityModal.classList.remove('active');
            chatInput.value = `Tell me the best places, 2-day travel plan, and famous foods in ${city}`;
            handleSendMessage();
        });

        // Copy buttons inside modal
        document.querySelectorAll('.copy-code-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.dataset.copy;
                navigator.clipboard.writeText(text);
                const original = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = original, 1800);
            });
        });

        // Export Chat
        exportChatBtn.addEventListener('click', exportConversation);

        // Mobile Sidebar Toggles
        if (menuToggle) {
            menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
        }
        if (closeSidebarBtn) {
            closeSidebarBtn.addEventListener('click', () => sidebar.classList.remove('open'));
        }

        // Voice button
        voiceBtn.addEventListener('click', toggleVoiceInput);

        // Instant Place Search
        if (placeSearchInput) {
            placeSearchInput.addEventListener('input', () => {
                const query = placeSearchInput.value.trim();
                if (query.length > 0) {
                    clearSearchBtn.style.display = 'block';
                } else {
                    clearSearchBtn.style.display = 'none';
                    searchDropdown.classList.remove('open');
                    searchDropdown.innerHTML = '';
                    return;
                }

                clearTimeout(searchDebounceTimer);
                searchDebounceTimer = setTimeout(async () => {
                    if (query.length < 2) return;
                    try {
                        const res = await fetch(`/api/places/search?q=${encodeURIComponent(query)}`);
                        const matches = await res.json();
                        renderSearchDropdown(matches);
                    } catch (err) {
                        console.error("Tourism search error:", err);
                    }
                }, 200);
            });

            placeSearchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const query = placeSearchInput.value.trim();
                    if (query) {
                        searchDropdown.classList.remove('open');
                        chatInput.value = query;
                        handleSendMessage();
                    }
                }
            });

            clearSearchBtn.addEventListener('click', () => {
                placeSearchInput.value = '';
                clearSearchBtn.style.display = 'none';
                searchDropdown.classList.remove('open');
                searchDropdown.innerHTML = '';
            });

            document.addEventListener('click', (e) => {
                if (searchBarWrapper && !searchBarWrapper.contains(e.target)) {
                    searchDropdown.classList.remove('open');
                }
            });
        }
    }

    function renderSearchDropdown(matches) {
        searchDropdown.innerHTML = '';
        if (!matches || matches.length === 0) {
            searchDropdown.innerHTML = `<div style="padding: 12px; font-size: 0.8rem; color: var(--text-dim); text-align: center;">No tourism information found matching "${placeSearchInput.value}"</div>`;
            searchDropdown.classList.add('open');
            return;
        }

        matches.forEach(p => {
            const item = document.createElement('div');
            item.className = 'search-item';
            item.innerHTML = `
                <div class="search-item-info">
                    <span class="search-item-title">${p.place_name}</span>
                    <span class="search-item-meta">
                        <span>📍 ${p.city}</span>
                        <span>⏰ ${p.timings || 'Daytime'}</span>
                        <span>🎫 ${p.entry_fee || 'Free'}</span>
                    </span>
                </div>
                <span class="search-item-tag">${p.category}</span>
            `;

            item.addEventListener('click', () => {
                searchDropdown.classList.remove('open');
                placeSearchInput.value = p.place_name;
                if (p.result_type === 'itinerary') {
                    setCityFilter(p.city);
                    chatInput.value = `Show me the ${p.duration_days}-day itinerary for ${p.city}, including the budget`;
                } else {
                    setCityFilter(p.city);
                    chatInput.value = `Tell me the complete visitor guide for ${p.place_name} in ${p.city}, including timings, entry fee, how to reach, and insider tips`;
                }
                handleSendMessage();
            });

            searchDropdown.appendChild(item);
        });

        searchDropdown.classList.add('open');
    }

    // --- SPEECH RECOGNITION (VOICE INPUT) ---
    function setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            voiceBtn.style.display = 'none';
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = activeLanguage === 'tamil' ? 'ta-IN' : 'en-IN';

        recognition.onstart = () => {
            isRecording = true;
            voiceBtn.classList.add('recording');
            chatInput.placeholder = "Listening... speak now";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = (chatInput.value ? chatInput.value + ' ' : '') + transcript;
            chatInput.focus();
        };

        recognition.onerror = (e) => {
            console.error("Speech recognition error:", e);
            stopVoiceInput();
        };

        recognition.onend = () => {
            stopVoiceInput();
        };
    }

    function toggleVoiceInput() {
        if (!recognition) return;
        if (isRecording) {
            recognition.stop();
        } else {
            try {
                recognition.lang = activeLanguage === 'tamil' ? 'ta-IN' : 'en-IN';
                recognition.start();
            } catch (err) {
                console.error("Could not start speech recognition:", err);
            }
        }
    }

    function stopVoiceInput() {
        isRecording = false;
        voiceBtn.classList.remove('recording');
        chatInput.placeholder = "Ask about any subject, or try: 'ippo enna time?' / 'Explain photosynthesis'...";
    }

    // --- OLLAMA STATUS CHECK ---
    async function fetchOllamaStatus() {
        try {
            const res = await fetch('/api/ollama/status');
            const data = await res.json();

            if (data.online) {
                statusDot.className = 'status-indicator-dot online';
                const modelUsed = data.default_model || 'Local LLM';
                engineName.textContent = `Ollama Online (${modelUsed})`;
                engineMeta.textContent = `${data.models.length} model(s) available`;

                // Update model select if models are available
                if (data.models && data.models.length > 0) {
                    modelSelect.innerHTML = '';
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m;
                        opt.textContent = m;
                        if (m === data.default_model) opt.selected = true;
                        modelSelect.appendChild(opt);
                    });
                    activeModel = modelSelect.value;
                }
            } else {
                statusDot.className = 'status-indicator-dot offline';
                engineName.textContent = 'Local Knowledge Mode';
                engineMeta.textContent = 'Ollama Offline • Click for setup';
            }
        } catch (err) {
            statusDot.className = 'status-indicator-dot offline';
            engineName.textContent = 'Local Knowledge Mode';
            engineMeta.textContent = 'Ollama Offline • Click for setup';
        }
    }

    // --- DESTINATIONS API ---
    async function fetchDestinations() {
        try {
            const res = await fetch('/api/destinations');
            destinationsData = await res.json();
            renderDestinationList(destinationsData);
        } catch (err) {
            console.error("Failed to fetch destinations:", err);
        }
    }

    function renderDestinationList(groupedData) {
        destinationList.innerHTML = '';
        let totalCount = 0;

        for (const [state, cities] of Object.entries(groupedData)) {
            cities.forEach(c => {
                totalCount++;
                const item = document.createElement('div');
                item.className = `dest-item ${activeCityFilter === c.city ? 'active' : ''}`;
                item.innerHTML = `
                    <span class="dest-name">📍 ${c.city}</span>
                    <span class="dest-count">${c.place_count} spots</span>
                `;
                item.addEventListener('click', () => {
                    setCityFilter(c.city);
                    openCityModal(c.city);
                });
                destinationList.appendChild(item);
            });
        }
        destTotalCount.textContent = `${totalCount} Cities`;
    }

    function filterDestinationsByCategory(category) {
        // Quick thematic filter
        if (category === 'all') {
            setCityFilter(null);
            return;
        }
        const mapping = {
            'hill': 'Ooty',
            'temple': 'Madurai',
            'beach': 'Chennai',
            'nature': 'Kodaikanal'
        };
        const targetCity = mapping[category];
        if (targetCity) {
            setCityFilter(targetCity);
            chatInput.value = `Tell me the top ${category === 'hill' ? 'hill stations and viewpoints' : category} in and around ${targetCity}`;
            chatInput.focus();
        }
    }

    function setCityFilter(city) {
        activeCityFilter = city;
        if (city) {
            activeFilterStrip.style.display = 'flex';
            filterValueText.textContent = city;
            activeDestBadge.textContent = `${city} (Focused)`;
        } else {
            activeFilterStrip.style.display = 'none';
            activeDestBadge.textContent = 'All Destinations (Tamil Nadu)';
        }

        // Highlight in destination list
        document.querySelectorAll('.dest-item').forEach(item => {
            if (city && item.textContent.includes(city)) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // --- CITY DEEP DIVE MODAL ---
    async function openCityModal(city) {
        cityModalTitle.textContent = city;
        cityModalIcon.textContent = city === 'Ooty' ? '🏔️' : (city === 'Chennai' ? '🏖️' : (city === 'Madurai' ? '🛕' : '📍'));
        cityPlacesGrid.innerHTML = '<div class="loading-shimmer-mini">Loading verified attractions...</div>';
        cityModalItinerary.innerHTML = '<div class="loading-shimmer-mini">Loading curated itinerary...</div>';
        cityModal.classList.add('active');

        try {
            const res = await fetch(`/api/destinations/${encodeURIComponent(city)}`);
            const data = await res.json();

            // Render Itinerary summary
            if (data.itineraries && data.itineraries.length > 0) {
                const itin = data.itineraries[0];
                const plan = itin.plan || {};
                let daysHtml = '';
                if (plan.days) {
                    daysHtml = plan.days.map(d => `
                        <div style="margin-top: 8px;">
                            <strong>Day ${d.day}: ${d.title}</strong>
                            <p style="font-size: 0.82rem; margin: 4px 0;">🌅 Morning: ${d.morning}</p>
                            <p style="font-size: 0.82rem; margin: 4px 0;">☀️ Afternoon: ${d.afternoon}</p>
                            <p style="font-size: 0.82rem; margin: 4px 0;">🌆 Evening: ${d.evening}</p>
                        </div>
                    `).join('');
                }
                cityModalItinerary.innerHTML = `
                    <h4 style="color: var(--text-emerald); margin-bottom: 6px;">🗓️ Curated ${itin.duration_days}-Day Plan: ${itin.title}</h4>
                    <p style="font-size: 0.85rem; color: var(--text-muted);">${plan.summary || itin.description || ''}</p>
                    ${daysHtml}
                    <div style="margin-top: 10px; font-size: 0.8rem; color: var(--text-amber);">💰 Budget: ${itin.estimated_budget || 'Budget friendly'}</div>
                `;
            } else {
                cityModalItinerary.innerHTML = `<p style="font-size: 0.85rem; color: var(--text-dim);">No fixed multi-day itinerary template. Chat with LocalLens for a personalized plan!</p>`;
            }

            // Render Places
            if (data.places && data.places.length > 0) {
                cityPlacesGrid.innerHTML = data.places.map(p => `
                    <div class="inline-place-card" style="min-width: unset; max-width: unset;">
                        <div class="inline-card-header">
                            <span class="inline-card-title">${p.place_name}</span>
                            <span class="inline-card-category">${p.category}</span>
                        </div>
                        <p class="inline-card-desc">${p.description}</p>
                        <div class="inline-card-meta">
                            <span>⏰ Timings: ${p.timings || 'General hours'}</span>
                            <span>🎫 Fee: ${p.entry_fee || 'Free'}</span>
                            ${p.famous_food ? `<span>🍲 Food: ${p.famous_food}</span>` : ''}
                        </div>
                        <button class="inline-card-action" onclick="window.askAboutPlace('${p.place_name}', '${city}')">Ask Details 💬</button>
                    </div>
                `).join('');
            } else {
                cityPlacesGrid.innerHTML = `<p>No places found.</p>`;
            }

        } catch (err) {
            cityPlacesGrid.innerHTML = `<p style="color: var(--rose-accent);">Error loading city details.</p>`;
        }
    }

    // Expose place ask handler to window
    window.askAboutPlace = (placeName, city) => {
        cityModal.classList.remove('active');
        chatInput.value = `Tell me more details about visiting ${placeName} in ${city}, best time, and tips.`;
        handleSendMessage();
    };

    // --- CHAT MESSAGING ---
    async function handleSendMessage() {
        const text = chatInput.value.trim();
        if (!text || isWaitingForResponse) return;

        isWaitingForResponse = true;
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Hide welcome hero
        welcomeHero.style.display = 'none';

        // Render User Message
        appendMessage('user', text);

        // Show Typing Indicator
        typingIndicator.style.display = 'flex';
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const payload = {
                message: text,
                session_id: currentSessionId,
                model: activeModel,
                city_filter: activeCityFilter,
                language: activeLanguage
            };

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            // Hide Typing Indicator
            typingIndicator.style.display = 'none';

            if (data.reply) {
                appendMessage('bot', data.reply, data.places, data.model_used);
                fetchSessionsList();
            } else if (data.error) {
                appendMessage('bot', `⚠️ Sorry, an error occurred: ${data.error}`);
            }
        } catch (err) {
            typingIndicator.style.display = 'none';
            appendMessage('bot', `⚠️ Could not reach LocalLens backend server. Please verify app.py is running.`);
            console.error("Chat error:", err);
        } finally {
            isWaitingForResponse = false;
            chatInput.focus();
        }
    }

    function appendMessage(sender, text, places = [], modelUsed = null) {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '👤' : '✦';

        const content = document.createElement('div');
        content.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // Parse markdown or use fallback
        bubble.innerHTML = renderMarkdown(text);

        content.appendChild(bubble);

        // If places are attached, render rich cards carousel
        if (places && places.length > 0) {
            const carousel = document.createElement('div');
            carousel.className = 'cards-carousel';

            places.forEach(p => {
                const card = document.createElement('div');
                card.className = 'inline-place-card';
                card.innerHTML = `
                    <div class="inline-card-header">
                        <span class="inline-card-title">${p.place_name}</span>
                        <span class="inline-card-category">${p.category}</span>
                    </div>
                    <p class="inline-card-desc">${p.description}</p>
                    <div class="inline-card-meta">
                        <span>⏰ ${p.timings || 'Daytime'}</span>
                        <span>🎫 ${p.entry_fee || 'Free entry'}</span>
                    </div>
                    <button class="inline-card-action">Details & Route →</button>
                `;
                card.querySelector('.inline-card-action').addEventListener('click', () => {
                    chatInput.value = `Tell me the route, best timing, and tips for ${p.place_name} in ${p.city}`;
                    handleSendMessage();
                });
                carousel.appendChild(card);
            });

            content.appendChild(carousel);
        }

        // Action Bar for Bot Messages
        if (sender === 'bot') {
            const actions = document.createElement('div');
            actions.className = 'message-actions';

            // Copy button
            const copyBtn = document.createElement('button');
            copyBtn.className = 'msg-action-btn';
            copyBtn.innerHTML = '📋 Copy';
            copyBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(text);
                copyBtn.innerHTML = '✅ Copied!';
                setTimeout(() => copyBtn.innerHTML = '📋 Copy', 1800);
            });

            // Speak button (TTS)
            const speakBtn = document.createElement('button');
            speakBtn.className = 'msg-action-btn';
            speakBtn.innerHTML = '🔊 Read Aloud';
            speakBtn.addEventListener('click', () => speakText(text, speakBtn));

            actions.appendChild(copyBtn);
            actions.appendChild(speakBtn);

            if (modelUsed) {
                const modelBadge = document.createElement('span');
                modelBadge.className = 'msg-model-badge';
                modelBadge.textContent = modelUsed;
                actions.appendChild(modelBadge);
            }

            content.appendChild(actions);
        }

        if (sender === 'user') {
            wrapper.appendChild(content);
            wrapper.appendChild(avatar);
        } else {
            wrapper.appendChild(avatar);
            wrapper.appendChild(content);
        }

        messagesList.appendChild(wrapper);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // --- MARKDOWN RENDERER ---
    function renderMarkdown(rawText) {
        if (window.marked && typeof window.marked.parse === 'function') {
            return window.marked.parse(rawText);
        }
        // Fallback basic regex markdown
        return rawText
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/`([^`]+)`/gim, '<code>$1</code>')
            .replace(/^\s*\n\*/gm, '<ul>\n*')
            .replace(/^(\*.+)\s*\n([^\*])/gm, '$1\n</ul>\n\n$2')
            .replace(/^\*(.+)/gm, '<li>$1</li>')
            .replace(/\n$/gim, '<br />')
            .replace(/\n\n/gim, '<br /><br />');
    }

    // --- TEXT TO SPEECH (TTS) ---
    function speakText(text, btnElement) {
        if (!window.speechSynthesis) return;

        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            btnElement.innerHTML = '🔊 Read Aloud';
            return;
        }

        // Clean markdown for speech
        const cleanText = text.replace(/[*#`_>\[\]]/g, '').slice(0, 400);
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        btnElement.innerHTML = '⏹️ Stop';
        utterance.onend = () => { btnElement.innerHTML = '🔊 Read Aloud'; };
        utterance.onerror = () => { btnElement.innerHTML = '🔊 Read Aloud'; };

        window.speechSynthesis.speak(utterance);
    }

    // --- CHAT SESSIONS MANAGEMENT ---
    async function loadSession(sessionId) {
        currentSessionId = sessionId;
        localStorage.setItem('locallens_session_id', sessionId);
        messagesList.innerHTML = '';

        try {
            const res = await fetch(`/api/sessions/${sessionId}`);
            const messages = await res.json();

            if (messages && messages.length > 0) {
                welcomeHero.style.display = 'none';
                messages.forEach(m => {
                    let places = [];
                    let modelUsed = null;
                    if (m.meta_json) {
                        try {
                            const meta = JSON.parse(m.meta_json);
                            modelUsed = meta.model_used;
                        } catch (e) {}
                    }
                    appendMessage(m.sender, m.message, places, modelUsed);
                });
            } else {
                welcomeHero.style.display = 'flex';
            }
        } catch (err) {
            welcomeHero.style.display = 'flex';
        }
    }

    async function fetchSessionsList() {
        try {
            const res = await fetch('/api/sessions');
            const sessions = await res.json();
            renderSessionsList(sessions);
        } catch (err) {
            console.error("Could not fetch sessions:", err);
        }
    }

    function renderSessionsList(sessions) {
        historyList.innerHTML = '';
        if (!sessions || sessions.length === 0) {
            historyList.innerHTML = `<div class="empty-history">No conversations yet</div>`;
            return;
        }

        sessions.forEach(s => {
            const item = document.createElement('div');
            item.className = `history-item ${s.session_id === currentSessionId ? 'active' : ''}`;
            item.innerHTML = `
                <span class="history-title" title="${s.title}">${s.title}</span>
                <button class="history-delete-btn" title="Delete conversation">✕</button>
            `;

            item.querySelector('.history-title').addEventListener('click', () => {
                loadSession(s.session_id);
                fetchSessionsList();
                if (window.innerWidth <= 768) sidebar.classList.remove('open');
            });

            item.querySelector('.history-delete-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm("Delete this chat?")) {
                    await fetch(`/api/sessions/${s.session_id}`, { method: 'DELETE' });
                    if (s.session_id === currentSessionId) {
                        startNewChat();
                    } else {
                        fetchSessionsList();
                    }
                }
            });

            historyList.appendChild(item);
        });
    }

    function startNewChat() {
        currentSessionId = generateUUID();
        localStorage.setItem('locallens_session_id', currentSessionId);
        messagesList.innerHTML = '';
        welcomeHero.style.display = 'flex';
        setCityFilter(null);
        fetchSessionsList();
        chatInput.value = '';
        chatInput.focus();
        if (window.innerWidth <= 768) sidebar.classList.remove('open');
    }

    // --- EXPORT CONVERSATION ---
    function exportConversation() {
        const messages = Array.from(document.querySelectorAll('.message-wrapper')).map(w => {
            const isUser = w.classList.contains('user');
            const text = w.querySelector('.message-bubble').innerText;
            return `[${isUser ? 'USER' : 'LOCALLENS AI'}]:\n${text}\n`;
        }).join('\n----------------------------------------\n\n');

        if (!messages) {
            alert("No messages to export yet!");
            return;
        }

        const blob = new Blob([`# LocalLens AI Travel Itinerary & Conversation\n\n${messages}`], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `LocalLens_Travel_Plan_${new Date().toISOString().slice(0, 10)}.md`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // --- UTILITIES ---
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
});
