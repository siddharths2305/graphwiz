import re
import sys
from pathlib import Path

from graphviz import Source


def sanitize_label(text: str, max_len: int = 60) -> str:
    cleaned = (text or "Step").replace('"', "'").replace("\\", "/")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 3].rstrip() + "..."
    return cleaned


def extract_markdown_steps(markdown_text: str):
    text = (markdown_text or "").strip()
    if not text:
        return "Generated Workflow", ["Start", "End"]

    title = "Generated Workflow"
    steps = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            steps.append(line[3:].strip())
        elif line.startswith("### "):
            steps.append(line[4:].strip())
        elif re.match(r"^\d+[.)]\s+", line):
            steps.append(re.sub(r"^\d+[.)]\s+", "", line).strip())
        elif line.startswith("- ") or line.startswith("* "):
            steps.append(line[2:].strip())

    if not steps:
        return title, ["Define the goal", "Build the workflow", "Validate the output"]

    cleaned_steps = [step for step in steps if step]
    return title, cleaned_steps


def markdown_to_dot(markdown_text: str) -> str:
    title, steps = extract_markdown_steps(markdown_text)
    title_label = sanitize_label(title)
    node_labels = [title_label] + [sanitize_label(step) for step in steps]

    lines = [
        "digraph Workflow {",
        "    rankdir=TB;",
        "    graph [splines=ortho, nodesep=0.6, ranksep=0.9, pad=0.3];",
        '    node [shape=box, style="rounded,filled", fillcolor="#EAF2FF", color="#3A6EA5", fontname="Arial", penwidth=1.2];',
        '    edge [color="#3A6EA5", penwidth=1.4, arrowsize=0.8];',
        '    start [label="Start", shape=circle, fillcolor="#E8F5E9", color="#2E7D32"];',
        '    end [label="End", shape=circle, fillcolor="#FDECEA", color="#C62828"];',
    ]

    for index, label in enumerate(node_labels):
        node_id = f"n{index}"
        fill = "#FFF8E1" if index % 2 == 0 else "#E3F2FD"
        lines.append(f'    {node_id} [label="{label}", fillcolor="{fill}"];')

    lines.append("    start -> n0;")
    for index in range(1, len(node_labels)):
        previous = f"n{index - 1}"
        current = f"n{index}"
        lines.append(f"    {previous} -> {current};")
    lines.append("    n{last} -> end;".format(last=len(node_labels) - 1))
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_markdown_to_svg(markdown_text: str) -> str:
    dot_source = markdown_to_dot(markdown_text)
    return Source(dot_source).pipe(format="svg").decode("utf-8")


def convert_markdown_file(input_path: str | Path, output_path: str | Path | None = None) -> str:
    source = Path(input_path)
    markdown_text = source.read_text(encoding="utf-8")

    if output_path is None:
        target = source.with_suffix(".svg")
    else:
        target = Path(output_path)

    svg_text = render_markdown_to_svg(markdown_text)
    target.write_text(svg_text, encoding="utf-8")
    return str(target)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python graphwiz.py input.md [output.svg]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    result = convert_markdown_file(input_file, output_file)
    print(f"SVG generated: {result}")
