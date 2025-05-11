# YouTube Video Summary Suite

A next-generation, full-stack solution for intelligent, multi-language summarization of YouTube videos.  
Combining state-of-the-art LLMs, robust transcript extraction, and a modern web interface, this project empowers users to unlock insights from any YouTube content—instantly and interactively.

---

## ✨ Features

- **Seamless YouTube Integration**: Paste any YouTube URL and receive structured, timestamped summaries in your preferred language.
- **Intelligent Transcript Retrieval**: Dual-method backend leverages both the official YouTube transcript API and advanced yt-dlp extraction with cookie-based authentication for maximum coverage.
- **LLM-Powered Summaries**: Summaries are generated using cutting-edge large language models (Claude, GPT-4o, etc.), with prompt engineering for clarity, structure, and language specificity.
- **Interactive Frontend**: Modern Next.js web app with React and TailwindCSS, featuring an embedded video player, clickable transcript navigation, and real-time summary display.
- **Multi-Language Support**: Generate summaries in English, Chinese, and more, with language-aware formatting and requirements.
- **Automatic Fallback & Caching**: Robust fallback logic and centralized cache management ensure reliability and efficiency, even for restricted or region-locked videos.
- **Extensible & Maintainable**: Modular architecture for easy extension—add new transcript providers, summary types, or LLMs with minimal effort.

---

## 🗂️ Project Structure

- `frontend/` — Next.js + React web application (UI, video player, summary display)
- `backend/` — FastAPI server (transcript extraction, LLM integration, caching, API)
- `transcripts_cache/` — Centralized cache for transcripts, metadata, and cookies

---

## 🚀 Quick Start

1. **Clone the repository**
2. **Install dependencies**
   - Frontend: `cd frontend && npm install`
   - Backend: `cd backend && pip install -r requirements.txt`
3. **(Optional) Export YouTube cookies for restricted content**
   - Use `yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com/"`
   - Place `cookies.txt` in `backend/transcripts_cache/`
4. **Run the backend**
   - `cd backend && uvicorn main:app --reload`
5. **Run the frontend**
   - `cd frontend && npm run dev`
6. **Open your browser and enjoy!**

---

## 🧠 How It Works

- **Transcript Extraction**:  
  The backend first attempts to fetch transcripts using the official YouTube API. If unavailable, it falls back to yt-dlp, optionally using browser cookies for authentication.
- **Summary Generation**:  
  Extracted transcripts are formatted and sent to an LLM with carefully engineered prompts, producing structured, timestamped, and language-specific summaries.
- **Frontend Experience**:  
  Users interact with a sleek web UI, paste YouTube links, select summary type/language, and instantly receive interactive, navigable summaries.

---

## 🛡️ Best Practices & Notes

- **Keep cookies.txt up to date** for best access to restricted videos.
- **Cache auto-cleans** after 7 days, but you may review `transcripts_cache/` for compliance/security.
- **Test with public videos** to isolate issues unrelated to authentication.
- **Prompt customization** is available in `backend/main.py` for advanced users.

---

## ⚠️ Limitations

- **Unavailable/Private/Deleted videos** cannot be summarized (no API or tool can bypass this).
- **Region/copyright locks** may still block access, even with cookies.
- **LLM output** may occasionally deviate from strict formatting; post-processing is recommended for production.

---

## 🛠️ Extending the System

- Add new transcript providers in `backend/utils/youtube_utils.py`
- Adjust cache retention in `CACHE_EXPIRE_SECONDS`
- Integrate new LLMs or prompt templates as needed

---

## 📬 Contact & Support

For advanced usage, bug reports, or feature requests, please open an issue or contact the maintainer. 