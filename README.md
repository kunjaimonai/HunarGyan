<p align="center">
  <img src="https://github.com/user-attachments/assets/b8ad5ab1-ab34-443b-b5da-de3d1b929713" alt="HunarGyan Logo" width="300">
</p>


# HunarGyan 🎨🤖🇮🇳  
**Smart Offline-First AI Assistant for Indian Artisans**

> Helping India’s weavers, potters, and woodworkers document, design, and market their craft—**offline**, in their **language**, with zero tech friction.

---

## 🌟 Overview

**HunarGyan** is an offline-first, hybrid AI assistant for Indian artisans. Built for low-connectivity environments and local language needs, it enables users to:

- 🎙️ Record craft processes (voice/text)
- 📢 Generate AI-powered marketing content
- 🎨 Get design ideas from sketches or prompts
- 🌐 Publish to the internet when available

All **core features work offline** with local AI models. Translation between Indian languages is handled by a **locally hosted Sarvam-M model**.

---

## 🔑 Core Features

| 🧱 Module | 💡 Capabilities |
|----------|----------------|
| 📊 **Dashboard** | View crafts, design ideas, and content created. Quick actions for creation. |
| 👤 **Artisan Profile** | Auto-generated artisan bio from past projects |
| 📄 **Craft Documentation** | Voice/text input + images + step-wise editing (offline) |
| 📢 **Marketing Content** | AI-generated social media posts, banners, and newsletters |
| 🎨 **Design Generator** | Upload sketch ➜ get suggestions, materials, references |
| 💾 **Saved Works** | Edit, export, share—all stored offline |
| 🌍 **Language Support** | Indian languages, voice + text input, powered by local translation |

---

## 🌐 Hybrid Model

| Function | Mode | Notes |
|----------|------|-------|
| 🧠 AI Content Generation | ✅ Offline | Uses local models (Stable Diffusion, text generation) |
| 🗣️ Speech-to-Text | ✅ Offline | Using Whisper |
| 🌐 Language Translation | ✅ Offline | Powered by Sarvam-M (locally hosted) |
| 📤 Social Media Publishing | 🌐 Online-only | Sync when internet is available |
| 🗃️ Storage | ✅ Offline | Local SQLite database |

> All AI features are available **offline**. Internet is only used for **optional publishing**.

---

## 🖥️ UI Glimpse

| Dashboard | Document Crafting | Marketing Generator |
|----------|-------------------|---------------------|
| ![Dashboard](https://via.placeholder.com/250x150?text=Dashboard) | ![Doc](https://via.placeholder.com/250x150?text=Craft+Document) | ![Marketing](https://via.placeholder.com/250x150?text=Marketing+Content) |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| 💻 Frontend | [Next.js](https://nextjs.org/) (PWA-enabled) |
| 🔧 Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| 🗣️ Speech Input | Whisper (offline) |
| 🌐 Translation | Sarvam-M (locally hosted, multi-language support) |
| 🎨 Visual AI | Stable Diffusion (offline) |
| 🗃️ Storage | SQLite (local DB) |
| 🌐 Connectivity | Offline-first, hybrid publishing model |

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/kunjaimonai/HunarGyan.git
cd HunarGyan


# 2. Backend Setup (FastAPI + AI models)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload



# 4. Frontend Setup (Next.js)
cd ../frontend
pnpm install
pnpm run dev
