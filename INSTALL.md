# AI Agent Studio Installation Guide

## Quick setup

```powershell
cd D:\AUTO_GRAPHWIZ
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Install Graphviz

Windows:

```powershell
winget install --id Graphviz.Graphviz --accept-source-agreements --accept-package-agreements
```

If Graphviz was installed manually, make sure the `dot` command is available in your PATH.

## Configure credentials

Create a `.env` file if you want to use environment variables:

```text
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Alternatively, you can place a key in `api_keys.gitignore` using this format:

```text
groq_api="your_api_key_here"
```

The app reads `GROQ_API_KEY` and `GROQ_MODEL` from the process environment, `.env`,
or `api_keys.gitignore` (for the API key). If `GROQ_MODEL` is omitted, it uses
`openai/gpt-oss-120b`, or automatically selects an available model if that model
is not enabled for the key.

## Launch the app

```powershell
cd D:\AUTO_GRAPHWIZ
.\.venv\Scripts\python.exe -m streamlit run main.py --server.address 127.0.0.1 --server.port 8502
```

Open:

```text
http://127.0.0.1:8502
```
