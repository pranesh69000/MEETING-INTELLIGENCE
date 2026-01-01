# 🎙️ Meeting Intelligence

> **Turn meetings into structured intelligence — automatically.**  
> Record. Transcribe. Summarize. Save. Done.

Meeting Intelligence is a **browser-based meeting intelligence system** that records meeting audio (system audio + microphone), transcribes it locally using AI, extracts summaries and action items and syncs **only the notes** to Google Drive.

Built out of pure curiosity and a deep interest in **AI-powered productivity tools**, this project focuses on doing the *core things really well* — without overengineering.

---

## ✨ Why Meeting Intelligence?

Meetings are full of insights, decisions and action items — but most of them get lost.

Meeting Intelligence helps you:
- 🎧 Record meetings locally (browser-based)
- 🧠 Convert speech to text using **local AI**
- 📝 Generate clean summaries & action items
- ☁️ Store notes safely in Google Drive
- 🔒 Keep privacy first (audio never leaves your system)



---

## 🚀 Core Features

- 🎙️ **Browser-based Recording**
  - Records **system audio + microphone**
  - Manual start & stop control

- 🧠 **Local Speech-to-Text**
  - Uses **OpenAI Whisper (base)** model locally
  - No API calls, no rate limits

- 👥 **Speaker-aware Transcription**
  - Basic speaker labeling for clarity

- 📝 **Smart Summaries & Action Items**
  - Clear, readable meeting notes
  - Focused on what actually matters

- ☁️ **Google Drive Sync**
  - Saves **only text notes**
  - No audio uploads (privacy-friendly)

- 💯 **Free & Open-Source Stack**
  - No paid tools
  - No subscriptions
  - Fully reproducible

---

## 🧱 Tech Stack

### Frontend
- ⚛️ **React**
- ⚡ **Vite**
- 🌐 Browser Media APIs

### Backend
- 🐍 **Python**
- 🎧 **FFmpeg** (for audio processing)
- 🧠 **Whisper (base model – local)**

### Storage
- ☁️ **Google Drive API**  
  *(Notes only — transcripts, summaries, action items)*

---


## ▶️ How to Run the Project

> ⚠️ Important: **Backend must be running before the frontend**

### 1️⃣ Start the Backend (Python)
- Handles:
  - Audio processing
  - Transcription
  - Summarization
  - Google Drive sync

### 2️⃣ Start the Frontend (React + Vite)
- User interface for:
  - Recording control
  - Viewing transcripts
  - Viewing summaries
  - Saving notes

Once both are running:
- Join your meeting
- Start recording
- End meeting
- Get structured notes ✨

---

## 🎯 What This Project Focuses On

- ✅ Accuracy over hype  
- ✅ Privacy-first design  
- ✅ Local execution  
- ✅ Clean, explainable pipeline  



---




## 🧠 Learning Outcomes

This project helped me deeply understand:
- Browser audio capture constraints
- AI model integration (local inference)
- End-to-end ML pipelines
- Privacy-aware system design
- Practical trade-offs in real products

---

## 📜 License

This project uses **free and open-source tools** and is intended for learning, experimentation and demonstration purposes.

---

## ⭐ Rate This Project

If you find this interesting or useful:
- ⭐ Star the repo
- 🍴 Fork it
- 💬 Share feedback

Every bit of feedback helps improve it further 🚀

---

**Built with curiosity, clarity and a love for solving real problems.**


