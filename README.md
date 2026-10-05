# 🧭 LocalLens AI — Local Assistant

> A private, local-first assistant for questions across subjects, with current local time and a curated South India tourism knowledge base. General answers use **Ollama Local LLM**; travel guides can fall back to **SQLite (RAG)**.
> No external AI API keys or cloud AI service are required.

---

## 🌟 Overview & Architecture

```text
                 USER
                   │
                   ▼
          ┌─────────────────┐
          │   CHATBOT UI    │
          │ (HTML5+CSS3+JS) │
          │  User Message   │
          │       ↓         │
          │  Bot Response   │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Python Backend  │
          │    app.py       │
          └────────┬────────┘
                   │
          ┌────────┴─────────┐
          ▼                  ▼
 ┌────────────────┐   ┌─────────────────┐
 │ Local Tourism  │   │   SQLite DB     │
 │ Knowledge Base │   │  Chat History   │
 └───────┬────────┘   └─────────────────┘
         │
         ▼
 ┌─────────────────────┐
 │ General-purpose     │
 │   Local LLM         │
 │      Ollama         │
 │  Llama 3.2 / Qwen   │
 └──────────┬──────────┘
            │
            ▼
       AI RESPONSE
```

---

## 📁 Project Structure

```text
LocalLens/
│
├── app.py              # Main Flask Backend with RAG pipeline & Ollama connector
├── seed_db.py          # Database seeding script for destinations & itineraries
├── tourism.db          # SQLite database (Places, Itineraries, Chat History)
├── requirements.txt    # Python package dependencies
├── README.md           # Documentation & setup manual
│
├── templates/
│   └── index.html      # Responsive Chatbot Web UI
│
└── static/
    ├── style.css       # Luxury Dark Mode & Glassmorphic Design System
    └── script.js       # Chat handling, Speech-to-Text, TTS, and Session manager
```

---

## 🚀 Key Features

1. **General-purpose local assistant**:
   - Answers academic, technical, professional, and everyday questions using an Ollama model running on the user's computer.
   - Responds in English, Tamil, or Tanglish based on the question.
   - Reports the computer's configured local time directly from Python's system clock, even when Ollama is offline.

2. **Intelligent Local RAG Knowledge Engine**:
   - Covers top tourist destinations across Tamil Nadu, Kerala, Pondicherry & Karnataka:
     - **Tamil Nadu**: Ooty, Kodaikanal, Chennai, Madurai, Rameshwaram, Kanyakumari, Thanjavur.
     - **Kerala**: Munnar, Wayanad.
     - **Pondicherry**: French Quarter, Rock Beach, Auroville.
   - Comprehensive attraction metadata: Timings, Entry fees, Best time to visit, Highlights, and Famous Local Delicacies.
   - Searches every destination and itinerary field, including descriptions, timings, fees, food, routes, nearby attractions, tips, budgets, and itinerary plans.
   - Matching database facts are used to answer questions even when Ollama is offline.

3. **Dual-Engine Architecture (Smart Fallback)**:
   - **Ollama Online**: Uses local LLM (`llama3.2:3b`, `qwen2.5`, etc.) for general questions and adds tourism facts when relevant.
   - **Ollama Offline**: Current-time and supported tourism questions work locally. Other subject answers require Ollama.

4. **Multi-Language Support**:
   - Fluent support for **English**, **தமிழ் (Tamil)**, and **Tanglish** (e.g., *"Ooty-la 2 days trip plan kudu"*).

5. **Modern High-End Aesthetics**:
   - Luxury Dark Canvas with vibrant Emerald & Golden travel accents.
   - Dynamic destination cards with quick explore triggers.
   - Interactive Place Cards embedded in chat messages with timings, entry fees, and "Details & Route" actions.
   - Web Speech API: Voice input (Speech-to-Text) & Read Aloud (Text-to-Speech).
   - Export conversation as a Markdown travel guide.
   - Chat history tracking with SQLite session persistence.

---

## 🛠️ Step-by-Step Installation & Run Guide

### STEP 1 — Virtual Environment (Recommended)

Open your terminal in the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

*(If PowerShell script execution is restricted, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

---

### STEP 2 — Install Python Dependencies

```powershell
pip install -r requirements.txt
```

---

### STEP 3 — Initialize Tourism Database

Create the local SQLite database with the curated destinations and itineraries:

```powershell
python seed_db.py
```

The generated `tourism.db` stays local because it also stores chat history.

---

### STEP 4 — Install & Run Ollama (Recommended for General Questions)

1. Download and install Ollama from [ollama.com](https://ollama.com).
2. Pull the lightweight Llama 3.2 3B model:
   ```powershell
   ollama pull llama3.2:3b
   ```
3. Start the Ollama server in a terminal:
   ```powershell
   ollama serve
   ```
   *(Keep this terminal open)*

---

### STEP 5 — Run LocalLens Chatbot Backend

In another terminal:

```powershell
python app.py
```

You will see:
```text
============================================================
[*] LocalLens Local Assistant Starting...
[*] Database: SQLite (tourism.db)
[*] Ollama Backend: http://localhost:11434 (Target Model: llama3.2:3b)
[*] Web UI available at: http://127.0.0.1:5000
============================================================
```

---

### STEP 6 — Open in Browser

Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 💬 Sample Prompts to Try

- **Current Time**: `"ippo enna time?"` — uses the computer's configured local clock.
- **General Knowledge**: `"Explain photosynthesis in simple terms"`
- **Programming**: `"Write a Python program to check whether a number is prime"`
- **Ooty 2-Day Plan**: `"Ooty-la 2 days trip plan kudu with best places, tea factory and budget"`
- **Madurai & Rameshwaram**: `"Plan a 3-day spiritual circuit for Madurai Meenakshi Temple and Rameshwaram Dhanushkodi"`
- **Chennai Coastal & Heritage**: `"What are the best historical places, temples, and beaches in Chennai?"`
- **Kodaikanal Weekend**: `"Suggest a misty weekend itinerary for Kodaikanal covering Pillar Rocks and Pine Forest"`
- **Tamil Query**: `"ஊட்டியில் 2 நாட்கள் சுற்றுலா செல்ல சிறந்த இடங்கள் மற்றும் பட்ஜெட் விவரங்கள் தருக"`
