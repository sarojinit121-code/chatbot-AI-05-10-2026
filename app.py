import os
import sys
import json
import sqlite3
import re
import uuid
from datetime import datetime

# Ensure UTF-8 output on Windows terminals
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'tourism.db')
OLLAMA_BASE_URL = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
DEFAULT_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
SEARCH_STOP_WORDS = {
    'the', 'and', 'for', 'are', 'what', 'when', 'where', 'why', 'how', 'who',
    'which', 'with', 'from', 'about', 'this', 'that', 'these', 'those', 'is',
    'was', 'were', 'be', 'been', 'being', 'to', 'of', 'in', 'on', 'at', 'by',
    'a', 'an', 'or', 'as', 'it', 'me', 'my', 'you', 'your', 'we', 'our',
    'can', 'could', 'would', 'should', 'do', 'does', 'did', 'tell', 'show',
    'give', 'find', 'search', 'please', 'want', 'need', 'best', 'places',
    'visit', 'trip', 'plan', 'details', 'information', 'info', 'all', 'any'
}
TRAVEL_SEARCH_TERMS = (
    'travel', 'trip', 'tour', 'visit', 'destination', 'itinerary', 'places',
    'beach', 'temple', 'சுற்றுலா', 'பயணம்', 'பார்க்க', 'இடங்கள்'
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def search_rows_by_fields(cursor, table, query, limit):
    """Rank matching records by how many query terms occur across their fields."""
    cursor.execute(f'PRAGMA table_info("{table}")')
    columns = [row['name'] for row in cursor.fetchall() if row['name'] != 'id']
    words = [
        word for word in re.findall(r'\b\w{3,}\b', query.lower())
        if word not in SEARCH_STOP_WORDS
    ]
    if not columns or not words:
        return []

    field_expressions = [
        f"LOWER(COALESCE(CAST(\"{column}\" AS TEXT), '') || ' {column.lower()}') LIKE ?"
        for column in columns
    ]
    term_conditions = [
        "(" + " OR ".join(field_expressions) + ")"
        for _ in words
    ]
    where_clause = " AND ".join(term_conditions)
    score_expression = " + ".join(
        f"CASE WHEN {condition} THEN 1 ELSE 0 END"
        for condition in term_conditions
    )
    term_params = [f"%{word}%" for word in words for _ in columns]
    cursor.execute(
        f"""
        SELECT *, ({score_expression}) AS _match_score
        FROM "{table}"
        WHERE {where_clause}
        ORDER BY _match_score DESC, id ASC
        LIMIT ?
        """,
        term_params + term_params + [limit]
    )
    results = []
    for row in cursor.fetchall():
        result = dict(row)
        result.pop('_match_score', None)
        results.append(result)
    return results

def check_ollama_status():
    """Checks if Ollama is running and lists downloaded models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=1.5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get('name') for m in data.get('models', [])]
            return {
                "online": True,
                "models": models,
                "default_model": DEFAULT_MODEL if DEFAULT_MODEL in models else (models[0] if models else DEFAULT_MODEL)
            }
    except Exception:
        pass
    return {
        "online": False,
        "models": [],
        "default_model": DEFAULT_MODEL
    }

def is_current_time_question(message):
    """Recognize common English, Tamil, and Tanglish requests for the current time."""
    text = message.lower()
    time_terms = ('time', 'neram', 'mani', 'மணி', 'நேரம்')
    current_terms = ('now', 'current', 'ippo', 'ippa', 'enna', 'sollu', 'என்ன', 'இப்போது', 'இப்போ', 'இப்ப')
    if not any(term in text for term in time_terms):
        return False
    if any(term in text for term in current_terms):
        return True
    return bool(re.search(
        r'\bwhat\s+time\s+is\s+it\b|'
        r"\bwhat(?:'s| is)\s+(?:the\s+)?time[?.!]*$|"
        r'\b(tell|show)\s+me\s+(?:the\s+)?time[?.!]*$',
        text
    ))

def current_time_reply(message, language):
    """Format the host's configured local time in the user's likely language."""
    now = datetime.now().astimezone()
    local_time = now.strftime('%I:%M:%S %p').lstrip('0')
    timezone = now.tzname() or now.strftime('%z')
    date = now.strftime('%Y-%m-%d')
    text = message.lower()
    tanglish_terms = ('ippo', 'ippa', 'enna', 'sollu', 'neram', 'mani')

    if 'tamil' in language.lower() or any(char in message for char in ('நேரம்', 'மணி', 'இப்போது', 'இப்போ')):
        return f"இப்போது உங்கள் கணினியின் உள்ளூர் நேரம் **{local_time}** ({timezone}), தேதி {date}."
    if 'tanglish' in language.lower() or any(term in text for term in tanglish_terms):
        return f"Ippo unga computer-la irukkura local time **{local_time}** ({timezone}), date {date}."
    return f"The current local time on this computer is **{local_time}** ({timezone}) on {date}."

def search_tourism_knowledge(query, city_filter=None):
    """
    Searches SQLite database for specific place, city, and itineraries.
    Prioritizes specific place queries (e.g., 'Doddabetta Peak', 'Marina Beach', 'Meenakshi Temple').
    """
    conn = get_db()
    cursor = conn.cursor()

    query_lower = query.lower()
    specific_place = None
    detected_city = None

    # Step A: Fetch all destinations to check for specific place mentions
    cursor.execute("SELECT * FROM destinations")
    all_places = [dict(row) for row in cursor.fetchall()]

    # Tamil keywords map for places & cities
    tamil_place_map = {
        'மீனாட்சி': 'Meenakshi Amman Temple',
        'மெரினா': 'Marina Beach',
        'மரினா': 'Marina Beach',
        'கபாலீஸ்வரர்': 'Kapaleeshwarar Temple, Mylapore',
        'தொட்டபெட்டா': 'Doddabetta Peak',
        'தனுஷ்கோடி': 'Dhanushkodi Ghost Town & Beach',
        'பாம்பன்': 'Pamban Rail Bridge',
        'விவேகானந்தர்': 'Vivekananda Rock Memorial',
        'திருவள்ளுவர்': 'Thiruvalluvar Statue',
        'பெரிய கோவில்': 'Brihadisvara Temple (Big Temple)',
        'பிரகதீஸ்வரர்': 'Brihadisvara Temple (Big Temple)',
        'ஆரோவில்': 'Auroville & Matrimandir',
        'மாமல்லபுரம்': 'Shore Temple',
        'மகாபலிபுரம்': 'Shore Temple',
        'பைக்காரா': 'Pykara Lake & Waterfalls',
        'தூண் பாறை': 'Pillar Rocks',
    }

    tamil_city_map = {
        'ஊட்டி': 'Ooty',
        'சென்னை': 'Chennai',
        'கொடைக்கானல்': 'Kodaikanal',
        'மதுரை': 'Madurai',
        'ராமேஸ்வரம்': 'Rameshwaram',
        'ராமேசுவரம்': 'Rameshwaram',
        'கன்னியாகுமரி': 'Kanyakumari',
        'தஞ்சாவூர்': 'Thanjavur',
        'தஞ்சை': 'Thanjavur',
        'பாண்டிச்சேரி': 'Pondicherry',
        'புதுச்சேரி': 'Pondicherry',
        'மூணார்': 'Munnar',
        'மாமல்லபுரம்': 'Mahabalipuram',
    }

    # Check Tamil place matches first
    for tk, target_name in tamil_place_map.items():
        if tk in query:
            for p in all_places:
                if p['place_name'] == target_name:
                    specific_place = p
                    detected_city = p['city']
                    break
        if specific_place:
            break

    # Check Tamil city matches
    if not detected_city:
        for tc, target_city in tamil_city_map.items():
            if tc in query:
                detected_city = target_city
                break

    # Check for direct or partial match with place names
    if not specific_place:
        for p in all_places:
            p_name = p['place_name'].lower()
            p_clean = re.sub(r'[^a-zA-Z0-9\s]', '', p_name)
            if p_clean in query_lower or p_name in query_lower:
                specific_place = p
                detected_city = p['city']
                break
            keywords = [k for k in p_clean.split() if len(k) >= 4 and k not in ('park', 'lake', 'falls', 'view', 'hall', 'road', 'town', 'rock', 'beach')]
            for kw in keywords:
                if kw in query_lower:
                    specific_place = p
                    detected_city = p['city']
                    break
            if specific_place:
                break

    # Step B: If no specific place found, check for known cities or city filter
    known_cities = ['ooty', 'chennai', 'kodaikanal', 'madurai', 'rameshwaram', 'kanyakumari', 'thanjavur', 'pondicherry', 'munnar', 'mahabalipuram']
    if not detected_city:
        if city_filter and city_filter.lower() in known_cities:
            detected_city = city_filter.strip().title()
        else:
            for c in known_cities:
                if c in query_lower:
                    detected_city = c.title()
                    break

    # Step C: Collect matching places
    places = []
    if specific_place:
        # Put the specific place first, followed by other spots in that city
        places.append(specific_place)
        cursor.execute("SELECT * FROM destinations WHERE LOWER(city) = LOWER(?) AND id != ? LIMIT 5",
                       (specific_place['city'], specific_place['id']))
        places.extend([dict(row) for row in cursor.fetchall()])
    elif detected_city:
        cursor.execute("SELECT * FROM destinations WHERE LOWER(city) = LOWER(?)", (detected_city,))
        places = [dict(row) for row in cursor.fetchall()]
    else:
        places = search_rows_by_fields(cursor, 'destinations', query, 10)

        if not places and any(term in query_lower for term in TRAVEL_SEARCH_TERMS):
            cursor.execute("SELECT * FROM destinations LIMIT 6")
            places = [dict(row) for row in cursor.fetchall()]

    # Step D: Itinerary Search
    itinerary = None
    days_match = re.search(r'(\d+)\s*(?:day|days)', query_lower)
    duration_days = int(days_match.group(1)) if days_match else 2

    target_city = detected_city if detected_city else (places[0]['city'] if places else None)
    if target_city and not specific_place:
        cursor.execute("SELECT * FROM itineraries WHERE LOWER(city) = LOWER(?) AND duration_days = ?", (target_city, duration_days))
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT * FROM itineraries WHERE LOWER(city) = LOWER(?) ORDER BY duration_days ASC LIMIT 1", (target_city,))
            row = cursor.fetchone()
    else:
        matching_itineraries = search_rows_by_fields(cursor, 'itineraries', query, 1)
        row = matching_itineraries[0] if matching_itineraries else None
    if row:
        itinerary = dict(row)
        try:
            itinerary['plan'] = json.loads(itinerary['plan_json'])
        except Exception:
            itinerary['plan'] = {}

    conn.close()
    return detected_city, places, itinerary, specific_place

def generate_place_deepdive_response(place, nearby_places, language="english"):
    """
    Generates a deep-dive, comprehensive travel dossier for a single specific tourist spot.
    Includes Overview, Timings, Entry fees, Best time, Highlights, How to reach, Insider tips, Food, and Nearby spots.
    """
    is_tamil = "tamil" in language.lower()
    is_tanglish = "tanglish" in language.lower()

    lines = []
    p_name = place['place_name']
    city = place['city']
    cat = place['category']
    tag = place.get('tag', 'Top Landmark')

    # Header
    if is_tamil:
        lines.append(f"### 🏛️ {p_name} — முழுமையான சுற்றுலா வழிகாட்டி & தகவல்கள்")
        lines.append(f"📍 **இடம்:** `{city}, {place['state']}` | 🏷️ **வகை:** `{cat}` | ⭐ **மதிப்பீடு:** `{tag}`\n")
        lines.append(f"📖 **விவரம்:** {place['description']}\n")
        lines.append("---")
        lines.append("#### 📋 பார்வையாளர் முக்கிய தகவல்கள் (Essential Info):")
        lines.append(f"- ⏰ **நேரங்கள் (Timings):** `{place.get('timings', 'பகல் நேரங்கள்')}`")
        lines.append(f"- 🎫 **நுழைவுக் கட்டணம் (Entry Fee):** `{place.get('entry_fee', 'இலவசம்')}`")
        lines.append(f"- 🗓️ **செல்ல சிறந்த காலம் (Best Time):** `{place.get('best_time', 'ஆண்டு முழுவதும்')}`")
        lines.append(f"- ✨ **முக்கிய சிறப்புகள் (Highlights):** {place.get('highlights', 'இயற்கைக் காட்சிகள்')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 🚗 எப்படி செல்வது? (How to Reach):")
        lines.append(f"{place.get('how_to_reach', f'இது {city} நகர மையத்திலிருந்து எளிதில் அடையக்கூடிய தொலைவில் உள்ளது.')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 💡 உள்ளூர் அனுபவக் குறிப்புகள் (Insider Pro-Tips):")
        lines.append(f"{place.get('insider_tips', 'காலை வேளையில் செல்வது சிறந்த அனுபவத்தைத் தரும்.')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 🍲 அருகில் புகழ்பெற்ற உணவு வகைகள் (Food Guide):")
        lines.append(f"{place.get('famous_food', 'அருகிலுள்ள உள்ளூர் சிற்றுண்டிகள் மற்றும் தேநீர்.')}")
        lines.append("")
        if place.get('nearby_attractions'):
            lines.append("---")
            lines.append("#### 📍 ஒரே பயணத்தில் இணைத்து பார்க்கக்கூடிய இடங்கள் (Nearby Attractions):")
            lines.append(f"{place['nearby_attractions']}")
            lines.append("")

    elif is_tanglish:
        lines.append(f"### 🏛️ {p_name} — Complete Spot Details & Visitor Guide")
        lines.append(f"📍 **Location:** `{city}, {place['state']}` | 🏷️ **Category:** `{cat}` | ⭐ **Tag:** `{tag}`\n")
        lines.append(f"📖 **Overview:** {place['description']}\n")
        lines.append("---")
        lines.append("#### 📋 Essential Spot Details:")
        lines.append(f"- ⏰ **Timings:** `{place.get('timings', 'Daytime')}`")
        lines.append(f"- 🎫 **Entry Fee:** `{place.get('entry_fee', 'Free')}`")
        lines.append(f"- 🗓️ **Best Time to Visit:** `{place.get('best_time', 'All seasons')}`")
        lines.append(f"- ✨ **Key Highlights:** {place.get('highlights', 'Scenic sightseeing')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 🚗 How to Reach & Route Guide:")
        lines.append(f"{place.get('how_to_reach', f'Easily accessible from {city} center via local cabs, autos, or buses.')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 💡 Pro-Tips for Visitors:")
        lines.append(f"{place.get('insider_tips', 'Early morning visit is recommended for pleasant weather.')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 🍲 Famous Food & Delicacies Nearby:")
        lines.append(f"{place.get('famous_food', 'Local tea, snacks and restaurants.')}")
        lines.append("")
        if place.get('nearby_attractions'):
            lines.append("---")
            lines.append("#### 📍 Nearby Spots to Combine in this trip:")
            lines.append(f"{place['nearby_attractions']}")
            lines.append("")

    else:
        lines.append(f"### 🏛️ {p_name} — Complete Destination Guide & Details")
        lines.append(f"📍 **Location:** `{city}, {place['state']}` | 🏷️ **Category:** `{cat}` | ⭐ **Tag:** `{tag}`\n")
        lines.append(f"📖 **Overview:** {place['description']}\n")
        lines.append("---")
        lines.append("#### 📋 Essential Visitor Information:")
        lines.append(f"- ⏰ **Opening Timings:** `{place.get('timings', 'Standard visiting hours')}`")
        lines.append(f"- 🎫 **Entry Fee & Tickets:** `{place.get('entry_fee', 'Free')}`")
        lines.append(f"- 🗓️ **Best Season / Hours to Visit:** `{place.get('best_time', 'All year round')}`")
        lines.append(f"- ✨ **Top Highlights & Activities:** {place.get('highlights', 'Scenic sightseeing')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 🚗 How to Reach & Route Guide:")
        lines.append(f"{place.get('how_to_reach', f'Located conveniently within {city}, easily reachable by auto, taxi, or local transit.')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 💡 Insider Pro-Tips for Travelers:")
        lines.append(f"{place.get('insider_tips', 'Visit during early hours or late afternoons for the finest experience.')}")
        lines.append("")
        lines.append("---")
        lines.append("#### 🍲 Famous Food & Delicacies Nearby:")
        lines.append(f"{place.get('famous_food', 'Local culinary specialties and fresh refreshments.')}")
        lines.append("")
        if place.get('nearby_attractions'):
            lines.append("---")
            lines.append("#### 📍 Nearby Attractions (Combine in same trip):")
            lines.append(f"{place['nearby_attractions']}")
            lines.append("")

    lines.append("\n> 💡 *Tip: Click any nearby spot card below or ask 'How to reach from Bangalore/Chennai' or 'Best hotels nearby' for more advice!*")
    return "\n".join(lines)

def generate_local_response(query, detected_city, places, itinerary, specific_place=None, language="english"):
    """
    Intelligent Local Knowledge Reasoning Engine.
    Used when Ollama is offline or as instant high-precision local guide response.
    """
    if specific_place:
        nearby = places[1:] if len(places) > 1 else []
        return generate_place_deepdive_response(specific_place, nearby, language)

    is_tamil = "tamil" in language.lower() or any(char in query for char in ['வணக்கம்', 'சுற்றுலா', 'ஊட்டி', 'சென்னை', 'திட்டம்'])
    is_tanglish = "tanglish" in language.lower() or any(word in query.lower() for word in ['enna', 'kudu', 'sollu', 'nalla', 'irukku', 'poganum', 'edam'])

    city_display = detected_city if detected_city else (
        places[0]['city'] if places else (itinerary.get('city') if itinerary else 'Tamil Nadu')
    )

    lines = []
    
    # Header greeting
    if is_tamil:
        lines.append(f"### 🌟 {city_display} சுற்றுலா வழிகாட்டி & பயணத் திட்டம்")
        lines.append(f"வணக்கம்! **{city_display}** உங்கள் பயணத்திற்கு மிகச் சிறந்த தேர்வு. உங்களுக்கான பிரத்யேக தகவல்கள் கீழே:")
    elif is_tanglish:
        lines.append(f"### 🌟 {city_display} Local Tourism Guide & Trip Plan")
        lines.append(f"Vanakkam! **{city_display}** trip-ku romba super choice. Ungalukaana detailed itinerary and top spots info idho:")
    else:
        lines.append(f"### 🌟 {city_display} Travel Guide & Curated Itinerary")
        lines.append(f"Welcome to your personalized **{city_display}** travel guide! Here are the finest local recommendations curated from our verified tourism knowledge base:")

    lines.append("")

    # If itinerary was found or requested
    if itinerary and 'plan' in itinerary and 'days' in itinerary['plan']:
        plan = itinerary['plan']
        lines.append(f"#### 🗓️ {itinerary.get('title', f'{city_display} Travel Plan')}")
        if plan.get('summary'):
            lines.append(f"*{plan['summary']}*\n")

        for d in plan.get('days', []):
            lines.append(f"---")
            lines.append(f"##### 📍 **Day {d.get('day')}: {d.get('title')}**")
            lines.append(f"- 🌅 **Morning:** {d.get('morning')}")
            lines.append(f"- ☀️ **Afternoon:** {d.get('afternoon')}")
            lines.append(f"- 🌆 **Evening:** {d.get('evening')}")
            if d.get('food_tip'):
                lines.append(f"- 🍽️ **Food Pick:** {d.get('food_tip')}")
            lines.append("")

        if plan.get('budget_estimate'):
            lines.append(f"💰 **Estimated Budget:** `{plan['budget_estimate']}`")
        if plan.get('travel_tip'):
            lines.append(f"💡 **Pro-Tip:** {plan['travel_tip']}")
        lines.append("")

    # Top places listing
    if places:
        lines.append(f"#### 🏛️ Top Places & Attractions in {city_display}:")
        for idx, p in enumerate(places[:6], 1):
            tag_badge = f" `[{p.get('tag', 'Top Spot')}]`" if p.get('tag') else ""
            lines.append(f"**{idx}. {p['place_name']}** ({p['category']}){tag_badge}")
            lines.append(f"   - 📖 *{p['description']}*")
            lines.append(f"   - ⏰ **Timings:** {p.get('timings', 'Standard hours')}")
            lines.append(f"   - 🎫 **Entry Fee:** {p.get('entry_fee', 'Free')}")
            lines.append(f"- 🗓️ **Best Time to Visit:** {p.get('best_time', 'All year round')}")
            lines.append(f"- ✨ **Highlights:** {p.get('highlights', 'Scenic views')}")
            if p.get('how_to_reach'):
                lines.append(f"   - 🚗 **Route:** {p['how_to_reach']}")
            if p.get('famous_food'):
                lines.append(f"   - 🍲 **Famous Food Nearby:** {p['famous_food']}")
            if p.get('nearby_attractions'):
                lines.append(f"   - 📍 **Nearby Attractions:** {p['nearby_attractions']}")
            if p.get('insider_tips'):
                lines.append(f"   - 💡 **Insider Tips:** {p['insider_tips']}")
            lines.append("")

    # Local Food Guide
    if places and places[0].get('famous_food'):
        lines.append("#### ☕ Local Delicacies to Experience:")
        foods = set()
        for p in places:
            if p.get('famous_food'):
                for f in p['famous_food'].split(','):
                    foods.add(f.strip())
        lines.append(" • " + " • ".join(list(foods)[:6]))
        lines.append("")

    lines.append("\n> 💡 *Note: Running with LocalLens Knowledge Engine. Start Ollama (`ollama serve`) with `llama3.2:3b` for live local LLM streaming responses.*")
    return "\n".join(lines)

def query_ollama(model, system_prompt, user_prompt):
    """Calls Ollama HTTP API with timeout and error handling."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=40)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('message', {}).get('content', '')
    raise Exception(f"Ollama returned HTTP {resp.status_code}: {resp.text}")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ollama/status', methods=['GET'])
def api_ollama_status():
    status = check_ollama_status()
    return jsonify(status)

@app.route('/api/destinations', methods=['GET'])
def api_destinations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT state, city, COUNT(*) as place_count 
        FROM destinations 
        GROUP BY state, city 
        ORDER BY state, city
    """)
    cities = [dict(row) for row in cursor.fetchall()]
    
    # Group by state
    grouped = {}
    for c in cities:
        state = c['state']
        if state not in grouped:
            grouped[state] = []
        grouped[state].append({
            "city": c['city'],
            "place_count": c['place_count']
        })
    conn.close()
    return jsonify(grouped)

@app.route('/api/destinations/<city>', methods=['GET'])
def api_city_places(city):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM destinations WHERE LOWER(city) = LOWER(?)", (city,))
    places = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM itineraries WHERE LOWER(city) = LOWER(?)", (city,))
    itineraries = []
    for row in cursor.fetchall():
        item = dict(row)
        try:
            item['plan'] = json.loads(item['plan_json'])
        except Exception:
            item['plan'] = {}
        itineraries.append(item)
        
    conn.close()
    return jsonify({"city": city, "places": places, "itineraries": itineraries})

@app.route('/api/places/search', methods=['GET'])
def api_search_places():
    """Live search across destination and itinerary fields for instant autocomplete."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor()
    results = search_rows_by_fields(cursor, 'destinations', q, 10)
    for result in results:
        result['result_type'] = 'place'
    itineraries = search_rows_by_fields(cursor, 'itineraries', q, 5)
    for itinerary in itineraries:
        itinerary['result_type'] = 'itinerary'
        itinerary['place_name'] = itinerary['title']
        itinerary['category'] = f"{itinerary['duration_days']}-day itinerary"
        itinerary['timings'] = f"{itinerary['duration_days']} days"
        itinerary['entry_fee'] = itinerary.get('estimated_budget')
    results.extend(itineraries)
    conn.close()
    return jsonify(results)

@app.route('/api/place/<int:place_id>', methods=['GET'])
def api_single_place(place_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM destinations WHERE id = ?", (place_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Place not found"}), 404
    return jsonify(dict(row))

@app.route('/api/sessions', methods=['GET'])
def api_sessions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.session_id, s.title, s.created_at, s.updated_at,
               COUNT(m.id) as message_count
        FROM chat_sessions s
        LEFT JOIN chat_messages m ON s.session_id = m.session_id
        GROUP BY s.session_id
        ORDER BY s.updated_at DESC
    """)
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(sessions)

@app.route('/api/sessions/<session_id>', methods=['GET'])
def api_session_messages(session_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(messages)

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def api_delete_session(session_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id') or str(uuid.uuid4())
    model = data.get('model') or DEFAULT_MODEL
    city_filter = data.get('city_filter')
    language = data.get('language', 'english')

    if not message:
        return jsonify({"error": "Message is empty"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Ensure session exists
    cursor.execute("SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,))
    if not cursor.fetchone():
        title = message[:40] + ("..." if len(message) > 40 else "")
        cursor.execute("INSERT INTO chat_sessions (session_id, title) VALUES (?, ?)", (session_id, title))
        conn.commit()

    # Save user message
    cursor.execute("INSERT INTO chat_messages (session_id, sender, message) VALUES (?, 'user', ?)",
                   (session_id, message))
    conn.commit()

    if is_current_time_question(message):
        reply = current_time_reply(message, language)
        meta = {
            "city": None,
            "places_count": 0,
            "is_specific_place": False,
            "place_name": None,
            "has_itinerary": False,
            "is_ollama": False,
            "model_used": "System Clock"
        }
        cursor.execute("""
            INSERT INTO chat_messages (session_id, sender, message, meta_json)
            VALUES (?, 'bot', ?, ?)
        """, (session_id, reply, json.dumps(meta)))
        cursor.execute(
            "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,)
        )
        conn.commit()
        conn.close()
        return jsonify({
            "reply": reply,
            "session_id": session_id,
            "places": [],
            "specific_place": None,
            "itinerary": None,
            "detected_city": None,
            "is_ollama": False,
            "model_used": "System Clock"
        })

    # Step 1: Query Local Knowledge Base
    detected_city, places, itinerary, specific_place = search_tourism_knowledge(message, city_filter)
    is_travel_question = (
        detected_city is not None
        or specific_place is not None
        or bool(places)
        or bool(itinerary)
        or any(term in message.lower() for term in TRAVEL_SEARCH_TERMS)
    )

    # Step 2: Attempt Ollama Generation
    ollama_info = check_ollama_status()
    reply = None
    is_ollama = False
    model_used = model

    if ollama_info['online']:
        available_models = ollama_info['models']
        target_model = model if model in available_models else (available_models[0] if available_models else model)
        
        # Include tourism facts only when the request is about travel.
        knowledge_context = []
        if is_travel_question and specific_place:
            knowledge_context.append(f"TARGET PLACE DEEP-DIVE: {specific_place['place_name']} in {specific_place['city']}, {specific_place['state']}")
            knowledge_context.append(
                "Verified Place Fields: "
                + json.dumps(specific_place, ensure_ascii=False, default=str)
            )
        elif is_travel_question:
            if detected_city:
                knowledge_context.append(f"Destination: {detected_city}")
            if places:
                knowledge_context.append("Verified Local Places Data:")
                for p in places[:8]:
                    knowledge_context.append(
                        "- " + json.dumps(p, ensure_ascii=False, default=str)
                    )
            if itinerary and 'plan' in itinerary:
                knowledge_context.append(
                    "Verified Itinerary Fields: "
                    + json.dumps(itinerary, ensure_ascii=False, default=str)
                )

        system_prompt = f"""You are LocalLens AI, a helpful general-purpose assistant.
Answer questions across academic, technical, professional, and everyday topics. Identify the subject from the question and give a clear, accurate, appropriately detailed answer. For coding requests, provide runnable code and explain how to use it; for projects, give practical implementation guidance.
Use natural Tamil or Tanglish when the user writes in Tamil or Tanglish, and English when the user writes in English. Be friendly and format longer answers with headings or bullet points.
Use the following local tourism facts only when they are relevant to the user's question. Do not force travel content into unrelated answers:
---
{chr(10).join(knowledge_context)}
---
Do not claim live information unless a connected live source is available. Do not invent details that are not supported by the supplied context."""

        try:
            reply = query_ollama(target_model, system_prompt, message)
            if reply:
                is_ollama = True
                model_used = target_model
        except Exception as e:
            print(f"Ollama call failed: {e}. Falling back to Local Engine.")
            reply = None

    # Step 3: Use the local tourism knowledge base when Ollama is unavailable.
    if not reply:
        if is_travel_question:
            reply = generate_local_response(message, detected_city, places, itinerary, specific_place, language)
            model_used = "LocalLens Knowledge Engine (RAG)"
        elif 'tamil' in language.lower() or any(char in message for char in ('என்ன', 'எப்படி', 'ஏன்')):
            reply = "பொதுவான பல்துறை கேள்விகளுக்கு உள்ளூர் Ollama AI model தேவை. Ollama-வை இயக்கி ஒரு model பதிவிறக்கம் செய்யுங்கள். நேரம் மற்றும் ஆதரிக்கப்படும் சுற்றுலா கேள்விகளுக்கு Ollama இல்லாமலும் பதில் கிடைக்கும்."
            model_used = "LocalLens Offline Assistant"
        elif 'tanglish' in language.lower() or any(word in message.lower() for word in ('enna', 'epdi', 'yen', 'sollu')):
            reply = "Pala different subjects-la answer panna local Ollama AI model venum. Ollama run panni oru model download pannunga. Current time-um supported tourism questions-um Ollama illamalum work aagum."
            model_used = "LocalLens Offline Assistant"
        else:
            reply = "General questions across subjects need a local Ollama model. Start Ollama and download a model to enable those answers. Current-time requests and supported tourism questions also work while Ollama is offline."
            model_used = "LocalLens Offline Assistant"

    # Step 4: Save bot message with metadata
    meta = {
        "city": detected_city,
        "places_count": len(places),
        "is_specific_place": bool(specific_place),
        "place_name": specific_place['place_name'] if specific_place else None,
        "has_itinerary": bool(itinerary),
        "is_ollama": is_ollama,
        "model_used": model_used
    }
    cursor.execute("""
        INSERT INTO chat_messages (session_id, sender, message, meta_json) 
        VALUES (?, 'bot', ?, ?)
    """, (session_id, reply, json.dumps(meta)))
    cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "reply": reply,
        "session_id": session_id,
        "places": places[:6],
        "specific_place": specific_place,
        "itinerary": itinerary,
        "detected_city": detected_city,
        "is_ollama": is_ollama,
        "model_used": model_used
    })

@app.route('/api/quick-prompts', methods=['GET'])
def api_quick_prompts():
    prompts = [
        {"icon": "🏔️", "title": "Doddabetta Peak", "prompt": "Doddabetta Peak timings, ticket fee, and best time to visit sollu", "city": "Ooty"},
        {"icon": "🏖️", "title": "Marina Beach", "prompt": "Marina Beach timings, lighthouse view, and famous street food pathi sollu", "city": "Chennai"},
        {"icon": "🌲", "title": "Pillar Rocks", "prompt": "Tell me about Pillar Rocks in Kodaikanal, mist timing, and how to reach", "city": "Kodaikanal"},
        {"icon": "🛕", "title": "Meenakshi Temple", "prompt": "Meenakshi Amman Temple 1000 pillar hall, timings and dress code details", "city": "Madurai"},
        {"icon": "🌊", "title": "Dhanushkodi", "prompt": "Dhanushkodi ghost town history, ocean view, and how to reach from Rameshwaram", "city": "Rameshwaram"},
        {"icon": "🥐", "title": "White Town", "prompt": "Pondicherry White Town French Quarter cycling and best cafes", "city": "Pondicherry"}
    ]
    return jsonify(prompts)

if __name__ == '__main__':
    print("=" * 60)
    print("[*] LocalLens Local Assistant Starting...")
    print("[*] Database: SQLite (tourism.db) with Deep-Dive Places")
    print(f"[*] Ollama Backend: {OLLAMA_BASE_URL} (Target Model: {DEFAULT_MODEL})")
    print("[*] Web UI available at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=False)
