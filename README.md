<div align="center">

# 🤖 AI Agent Studio

**Ask. Generate. Visualize. Export.**

A Streamlit-powered app that turns AI-generated responses into clean, exportable Graphviz workflow diagrams.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Graphviz](https://img.shields.io/badge/Graphviz-Diagrams-2E8B57?logo=graphviz&logoColor=white)](https://graphviz.org/)
[![Groq](https://img.shields.io/badge/Groq-API-F55036)](https://groq.com/)
[![License](https://img.shields.io/badge/License-Educational%20Use-lightgrey)](#license)

![AI Agent Studio demo](./assets/demo.gif)

</div>

---

## ✨ Overview

**AI Agent Studio** lets you ask a question, get an AI-generated response right in your browser, and turn that response into a **Graphviz workflow diagram** — all in a few clicks. It ships with a **Groq API** integration for fast generation, plus a **local fallback generator** so you're never blocked if the API is unavailable.

Perfect for quickly turning ideas, processes, or AI outputs into shareable diagrams and documentation.

## 📸 Screenshots

<div align="center">

| Ask a Question | Generated Workflow | Export Options |
|:---:|:---:|:---:|
| ![Prompt screen](./assets/screenshot-prompt.png) | ![Generated diagram](./assets/screenshot-diagram.png) | ![Export options](./assets/screenshot-export.png) |

</div>

## 🧩 Features

| Feature | Description |
|---|---|
| 💬 Prompt-based AI generation | Ask a question and get a response directly in the app |
| 📝 Markdown export | Save AI responses as `.md` files |
| 🔀 Markdown → Diagram | Convert Markdown or responses into Graphviz workflows |
| 🖼️ Multi-format export | Download diagrams as `.dot`, `.png`, and `.svg` |
| 📤 Upload & convert | Bring your own Markdown file and turn it into a diagram |
| 🔌 Offline fallback | Local flow generator kicks in if Groq is unavailable |

## 📁 Project Structure

```
AI-Agent-Studio/
├── main.py              # Streamlit application
├── graphwiz.py          # Standalone Markdown-to-DOT/SVG conversion script
├── tests/
│   └── test_app.py      # Regression tests
├── exports/             # Generated artifacts (gitignored)
├── .env.example         # Environment variable template
└── requirements.txt     # Python dependencies
```

## ✅ Requirements

- Python 3.10+
- [Graphviz](https://graphviz.org/download/) installed on your system
- A [Groq API key](https://console.groq.com/) (optional, but recommended)

## 🚀 Setup

**1. Open a terminal in the project folder**

**2. Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**4. Install Graphviz**

- Windows: install from https://graphviz.org/download/
- Or via winget:

```powershell
winget install --id Graphviz.Graphviz --accept-source-agreements --accept-package-agreements
```

**5. Add your Groq key**

Copy `.env.example` to `.env` and fill in the key, or for Streamlit Cloud, add it under **App settings → Secrets**.

```text
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub. **Do not commit** `.env`, `.streamlit/secrets.toml`, `api_keys.gitignore`, or any API key.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the main file to `main.py`.
4. Open the app settings **Secrets** section and add:

   ```toml
   GROQ_API_KEY = "your_new_groq_key_here"
   GROQ_MODEL = "openai/gpt-oss-120b"
   ```

The app reads these values from Streamlit Secrets in the cloud, or from `.env` and environment variables during local development. Generated files are created in `exports/` at runtime and are intentionally excluded from Git.

## ▶️ Run the App

```powershell
cd D:\AUTO_GRAPHWIZ
.\.venv\Scripts\python.exe -m streamlit run main.py --server.address 127.0.0.1 --server.port 8502
```

Then open:

```text
http://127.0.0.1:8502
```

## 🔀 Generate a Workflow from Markdown

<div align="center">

![Markdown to diagram conversion](./assets/markdown-to-diagram.gif)

</div>

Run the converter script directly:

```powershell
.\.venv\Scripts\python.exe graphwiz.py --input "exports\example.md" --output "exports\example.svg"
```

Or use the Python API directly:

```powershell
.\.venv\Scripts\python.exe -c "from graphwiz import convert_markdown_file; convert_markdown_file('exports\\example.md', 'exports\\example.svg')"
```

## 🧪 Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 📜 License

This project is for local educational and workflow-generation use.

---

<div align="center">

Made with ❤️ using Streamlit, Groq, and Graphviz

</div>
