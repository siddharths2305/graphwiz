import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from graphviz import Source


OUTPUT_DIR = Path("exports")
OUTPUT_DIR.mkdir(exist_ok=True)


def read_groq_api_key() -> str:
    env_key = os.getenv("GROQ_API_KEY") or os.getenv("groq_api")
    if env_key:
        return env_key.strip().strip('"\'')

    key_file = Path(__file__).with_name("api_keys.gitignore")
    if key_file.exists():
        try:
            content = key_file.read_text(encoding="utf-8")
            match = re.search(r'groq_api\s*=\s*["\']?([^"\'\n]+)["\']?', content)
            if match:
                key = match.group(1).strip()
                os.environ["GROQ_API_KEY"] = key
                return key
        except Exception:
            pass

    return ""


def sanitize_label(value: str, max_len: int = 72) -> str:
    text = (value or "Generated result").replace('"', "'").replace("\\", "/")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return text


def prepare_prompt_for_groq(prompt: str, max_chars: int = 4000) -> str:
    text = (prompt or "").strip()
    if not text:
        return ""
    if len(text) <= max_chars:
        return text

    trimmed = text[: max_chars - 12]
    if " " in trimmed:
        trimmed = trimmed.rsplit(" ", 1)[0]
    return (trimmed.strip() + "...") if trimmed.strip() else text[:max_chars].strip()


def generate_local_response(prompt: str) -> str:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return "Please enter a question or task to generate a response."

    answer = f"""# AI Response

You asked: {clean_prompt}

## Summary
This agent generated a response for your request using the local fallback workflow.

## Suggested next steps
1. Clarify the goal or audience.
2. Break the task into smaller phases.
3. Turn the answer into an implementation plan if needed.

## Example output
- Define the problem clearly.
- Gather required inputs and constraints.
- Create a solution flow.
- Validate the result with test cases.

## Final answer
The requested workflow can be planned, implemented, and documented with a clear structure. Start by defining the objective, the required inputs, and the final output, then build the system in small steps and validate each step before moving forward.
"""
    return answer


def generate_response(prompt: str) -> str:
    original_prompt = (prompt or "").strip()
    if not original_prompt:
        return "Please enter a question to continue."

    safe_prompt = prepare_prompt_for_groq(original_prompt)
    if safe_prompt != original_prompt:
        st.warning("Your prompt was too long for Groq, so it was shortened to fit the API size limit.")

    api_key = read_groq_api_key()
    model = os.getenv("GROQ_MODEL", "groq/compound")

    if api_key:
        try:
            from groq import Groq

            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": safe_prompt}],
                temperature=0.7,
                max_tokens=1200,
            )
            content = completion.choices[0].message.content
            if content:
                return content.strip()
        except Exception as exc:
            st.warning(f"Groq request failed: {exc}. Falling back to the local response generator.")

    return generate_local_response(original_prompt)


def build_flow_diagram(prompt: str, response: str | None = None) -> str:
    topic = sanitize_label((prompt or "AI workflow").strip() or "AI workflow")
    clean_response = sanitize_label((response or "Generated result").strip())

    dot = Source(
        f'''
        digraph AIFlow {{
            rankdir=LR;
            node [shape=box, style="rounded,filled", fillcolor="#EAF2FF", color="#3A6EA5", fontname="Arial"];
            edge [color="#3A6EA5", penwidth=1.5];

            start [label="Start"];
            input [label="User asks: {topic}"];
            agent [label="AI Agent"];
            analysis [label="Generate response"];
            output [label="Result: {clean_response}"];
            md [label="Export Markdown"];
            flow [label="Generate Graphviz Diagram"];
            end [label="Finish"];

            start -> input -> agent -> analysis -> output;
            output -> md;
            output -> flow;
            md -> end;
            flow -> end;
        }}
        '''
    )
    return dot.source


def generate_dot_from_markdown(markdown_text: str) -> str:
    text = (markdown_text or "").strip()
    if not text:
        return "digraph Workflow {\n  rankdir=LR;\n  start [label=\"Start\"];\n  end [label=\"End\"];\n  start -> end;\n}\n"

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = "Generated Workflow"
    steps = []

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            steps.append(line[3:].strip())
        elif line.startswith("### "):
            steps.append(line[4:].strip())
        elif re.match(r"^\d+\.\s+", line):
            steps.append(re.sub(r"^\d+\.\s+", "", line).strip())
        elif line.startswith("- "):
            steps.append(line[2:].strip())
        elif line.startswith("* "):
            steps.append(line[2:].strip())

    if not steps:
        steps = ["Understand the request", "Build the solution", "Validate the output"]

    labels = [sanitize_label(title)] + [sanitize_label(step) for step in steps if step]
    node_defs = []
    edge_defs = []

    for index, label in enumerate(labels):
        node_name = f"n{index}"
        fill = "#FFF8E1" if index % 2 == 0 else "#E3F2FD"
        node_defs.append(f'    {node_name} [label="{label}", fillcolor="{fill}"];')
        if index > 0:
            edge_defs.append(f"    n{index - 1} -> {node_name};")

    dot_lines = [
        "digraph Workflow {",
        "    rankdir=TB;",
        "    graph [splines=ortho, nodesep=0.6, ranksep=0.9, pad=0.3];",
        '    node [shape=box, style="rounded,filled", fillcolor="#EAF2FF", color="#3A6EA5", fontname="Arial", penwidth=1.2];',
        '    edge [color="#3A6EA5", penwidth=1.4, arrowsize=0.8];',
        '    start [label="Start", shape=circle, fillcolor="#E8F5E9", color="#2E7D32"];',
        '    end [label="End", shape=circle, fillcolor="#FDECEA", color="#C62828"];',
    ]
    dot_lines.extend(node_defs)
    dot_lines.append("    start -> n0;")
    dot_lines.extend(edge_defs)
    dot_lines.append("    n{last} -> end;".format(last=len(labels) - 1))
    dot_lines.append("}")
    return "\n".join(dot_lines) + "\n"


def format_markdown_output(prompt: str, response: str) -> str:
    title = (prompt or "Generated workflow").strip()
    if len(title) > 90:
        title = title[:87].rstrip() + "..."

    cleaned = (response or "").strip()
    if not cleaned:
        cleaned = "No response was generated."

    if cleaned.startswith("# "):
        body = cleaned
    else:
        intro = "## Overview\n\n" + cleaned.strip() + "\n"
        body = f"# {title}\n\n{intro}"

    if "## " not in body and "### " not in body:
        body = body + "\n## Key Workflow\n\n1. Define the goal and scope.\n2. Identify core inputs, actors, and decisions.\n3. Build the process flow in sequence.\n4. Validate output and iterate based on feedback.\n"

    return body.strip() + "\n"


def save_markdown_response(prompt: str, response: str) -> str:
    safe_name = "_".join((prompt or "response").lower().split())[:40] or "response"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{safe_name}_{timestamp}.md"
    output_path = OUTPUT_DIR / file_name
    formatted_md = format_markdown_output(prompt, response)
    output_path.write_text(formatted_md, encoding="utf-8")
    return str(output_path)


def render_dot_to_svg(dot_source: str) -> str:
    try:
        diagram = Source(dot_source)
        svg_data = diagram.pipe(format="svg")
        rendered = svg_data.decode("utf-8") if isinstance(svg_data, bytes) else str(svg_data)
        if rendered and "<svg" in rendered.lower():
            return rendered
    except Exception:
        pass

    message = "Graphviz is not installed on this system. Install Graphviz and restart the app to render the workflow diagram."
    return f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='300' viewBox='0 0 1200 300'>
      <rect width='1200' height='300' fill='#0f172a'/>
      <text x='600' y='140' text-anchor='middle' fill='#f8fafc' font-family='Arial' font-size='24'>Graphviz required for diagram rendering</text>
      <text x='600' y='175' text-anchor='middle' fill='#cbd5e1' font-family='Arial' font-size='16'>{message}</text>
    </svg>
    """.strip()


def save_flow_diagram(prompt: str, response: str, markdown_text: str | None = None) -> tuple[str, str, str]:
    safe_name = "_".join((prompt or "flow").lower().split())[:40] or "flow"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_text = markdown_text.strip() if markdown_text else response.strip()
    dot_source = generate_dot_from_markdown(source_text) if markdown_text else build_flow_diagram(prompt, response)
    dot_path = OUTPUT_DIR / f"{safe_name}_{timestamp}.dot"
    png_path = OUTPUT_DIR / f"{safe_name}_{timestamp}.png"
    svg_path = OUTPUT_DIR / f"{safe_name}_{timestamp}.svg"

    dot_path.write_text(dot_source, encoding="utf-8")

    try:
        diagram = Source(dot_source)
        diagram.render(outfile=str(png_path), cleanup=True, format="png")
    except Exception:
        png_path = OUTPUT_DIR / f"{safe_name}_{timestamp}.txt"
        png_path.write_text(dot_source, encoding="utf-8")

    try:
        svg_data = render_dot_to_svg(dot_source)
        svg_path.write_text(svg_data, encoding="utf-8")
    except Exception:
        svg_path.write_text(
            "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='200'><text x='50%' y='50%' text-anchor='middle' dominant-baseline='middle' font-family='Arial' font-size='20'>Graphviz is not installed. Install Graphviz to render the diagram.</text></svg>",
            encoding="utf-8",
        )

    return str(dot_path), str(png_path), str(svg_path)


def main() -> None:
    st.set_page_config(page_title="AI Agent Studio", page_icon="🤖", layout="wide")
    st.title("AI Agent Studio")
    st.caption("Ask anything, generate a response, and export a Markdown file plus a Graphviz flow diagram.")

    if "generated_answer" not in st.session_state:
        st.session_state.generated_answer = ""
    if "generated_prompt" not in st.session_state:
        st.session_state.generated_prompt = ""
    if "diagram_source" not in st.session_state:
        st.session_state.diagram_source = ""

    uploaded_md = st.file_uploader("Upload a Markdown file to convert into a Graphviz workflow", type=["md"], help="Optional: use an existing markdown file instead of the generated response.")
    with st.form("chat_form"):
        user_question = st.text_area("Ask your agent", height=120, placeholder="Example: Create a workflow for a customer onboarding system")
        submitted = st.form_submit_button("Generate response")

    if uploaded_md is not None:
        uploaded_text = uploaded_md.read().decode("utf-8")
        st.session_state.generated_answer = uploaded_text
        st.session_state.generated_prompt = uploaded_md.name
        st.session_state.diagram_source = generate_dot_from_markdown(uploaded_text)

    if submitted and user_question:
        answer = generate_response(user_question)
        st.session_state.generated_prompt = user_question
        st.session_state.generated_answer = answer
        st.session_state.diagram_source = generate_dot_from_markdown(format_markdown_output(user_question, answer))

    if st.session_state.generated_answer:
        st.subheader("Generated response")
        st.markdown(st.session_state.generated_answer)

        markdown_path = save_markdown_response(st.session_state.generated_prompt, st.session_state.generated_answer)
        dot_path, image_path, svg_path = save_flow_diagram(st.session_state.generated_prompt, st.session_state.generated_answer, st.session_state.generated_answer)

        col1, col2, col3 = st.columns(3)
        with col1:
            with open(markdown_path, "rb") as file:
                st.download_button(
                    label="Download .md",
                    data=file,
                    file_name=Path(markdown_path).name,
                    mime="text/markdown",
                )
        with col2:
            png_exists = Path(image_path).suffix.lower() == ".png"
            if png_exists:
                with open(image_path, "rb") as file:
                    st.download_button(
                        label="Download flow diagram (.png)",
                        data=file,
                        file_name=Path(image_path).name,
                        mime="image/png",
                    )
            else:
                with open(image_path, "rb") as file:
                    st.download_button(
                        label="Download DOT source",
                        data=file,
                        file_name=Path(image_path).name,
                        mime="text/plain",
                    )
        with col3:
            with open(svg_path, "rb") as file:
                st.download_button(
                    label="Download flow diagram (.svg)",
                    data=file,
                    file_name=Path(svg_path).name,
                    mime="image/svg+xml",
                )

        st.subheader("Flow diagram")
        try:
            st.graphviz_chart(st.session_state.diagram_source)
        except Exception:
            st.code(st.session_state.diagram_source)

        st.success(f"Files created in the exports folder: {Path(markdown_path).name}, {Path(dot_path).name}, {Path(image_path).name}, {Path(svg_path).name}")


if __name__ == "__main__":
    main()
