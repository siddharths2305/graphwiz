# AI Agent Studio

AI Agent Studio is a Streamlit-powered application that lets you:

- ask a question to an AI agent
- generate a response in the browser
- export the response as Markdown
- generate a Graphviz workflow from the Markdown or response
- download the resulting DOT, PNG, and SVG files

It is designed for quick workflow generation and documentation, with a Groq API integration and a local fallback response generator when the API is unavailable.

## Features

- Prompt-based AI generation
- Markdown export for saved responses
- Graphviz flow-generation from Markdown output
- SVG export for workflow diagrams
- Local fallback flow when Groq is unavailable
- Upload existing Markdown to convert into a diagram

## Project structure

- `main.py` — Streamlit application
- `graphwiz.py` — standalone Markdown-to-DOT/SVG conversion script
- `tests/test_app.py` — regression tests
- `exports/` — generated artifacts
- `.env.example` — environment variable template
- `requirements.txt` — Python dependencies

## Requirements

- Python 3.10+
- Graphviz installed on the system
- A Groq API key (optional but recommended)

## Setup

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Install Graphviz:

   - Windows: install from https://graphviz.org/download/
   - Or via winget:

   ```powershell
   winget install --id Graphviz.Graphviz --accept-source-agreements --accept-package-agreements
   ```

5. Add your Groq key:

   - Copy `.env.example` to `.env` and fill in the key, or
   - For Streamlit Cloud, add it under **App settings > Secrets**.

   Example:

   ```text
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   ```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub. Do not commit `.env`, `.streamlit/secrets.toml`,
   `api_keys.gitignore`, or any API key.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the main file to `main.py`.
4. Open the app settings **Secrets** section and add:

   ```toml
   GROQ_API_KEY = "your_new_groq_key_here"
   GROQ_MODEL = "openai/gpt-oss-120b"
   ```

The app reads these values from Streamlit Secrets in the cloud, or from `.env`
and environment variables during local development. Generated files are created
in `exports/` at runtime and are intentionally excluded from Git.

## Run the app

```powershell
cd D:\AUTO_GRAPHWIZ
.\.venv\Scripts\python.exe -m streamlit run main.py --server.address 127.0.0.1 --server.port 8502
```

Then open:

```text
http://127.0.0.1:8502
```

## Generate a workflow from Markdown

You can also run the converter script directly:

```powershell
.\.venv\Scripts\python.exe graphwiz.py --input "exports\example.md" --output "exports\example.svg"
```

If you prefer a more direct Python approach:

```powershell
.\.venv\Scripts\python.exe -c "from graphwiz import convert_markdown_file; convert_markdown_file('exports\\example.md', 'exports\\example.svg')"
```

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## License

This project is for local educational and workflow-generation use.
