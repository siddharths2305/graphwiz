# how to make ai agents that can create a graphwiz workflow diagram using  .md file

## Overview

Below is a **complete, step‑by‑step guide** for building an AI‑powered “agent” that reads a Markdown (`.md`) file, extracts a description of a workflow, and produces a Graphviz diagram (the same format that the `dot` language uses).  
The guide includes the overall design, the required tools, a minimal working prototype in Python, and tips for extending it into a more sophisticated AI‑driven system.

---

## 1. High‑level Architecture

```
+-------------------+        +-------------------+        +-------------------+
|  Markdown file    |  -->   |  Parsing Agent    |  -->   |  Graphviz Engine  |
|  (workflow.md)    |        |  (extract nodes   |        |  (dot → PNG/SVG) |
|                   |        |   & edges)        |        |                   |
+-------------------+        +-------------------+        +-------------------+
        ^                         ^                           ^
        |                         |                           |
        |                         |   (optional) AI model    |
        |                         |   (LLM to infer missing |
        |                         |    relationships)        |
        +-------------------------+---------------------------+
```

* **Parsing Agent** – a small program (or an LLM‑prompt) that reads the `.md` file and turns the textual description into a list of *nodes* and *edges*.  
* **Graphviz Engine** – the `graphviz` Python package (or the CLI) that takes the node/edge lists and renders a diagram.

---

## 2. Choose Your Toolchain

| Task | Recommended Library / Tool | Why |
|------|----------------------------|-----|
| Markdown parsing | `markdown`, `mistune`, or `commonmark` | Turns Markdown into an AST; you can walk the tree to find custom syntax. |
| Graph generation | `graphviz` (Python wrapper) | Simple API, produces `dot`, PNG, SVG, PDF, etc. |
| Optional AI inference | OpenAI GPT‑4, Claude, Llama‑2, etc. | If the Markdown only contains high‑level prose, an LLM can extract the workflow automatically. |
| Execution environment | Any Python 3.9+ runtime (local, Docker, cloud function) | Works everywhere; Graphviz binary must be installed (`apt-get install graphviz` or `brew install graphviz`). |

---

## 3. Define a Simple Markdown DSL (Domain‑Specific Language)

For a **minimal viable product** you can ask users to write the workflow in a very lightweight syntax that is easy to parse:

```markdown
# Example workflow.md

[Start]               # a node
[Validate Input]      # another node
[Process Data]        # another node
[Finish]              # final node

# Edges (directed)
[Start] -> [Validate Input]
[Validate Input] -> [Process Data]
[Process Data] -> [Finish]
```

*Lines that start with `[` and end with `]` are interpreted as **nodes**.  
Lines that contain `->` are interpreted as **directed edges**.*

You can of course enrich the DSL (add labels, colors, sub‑graphs, etc.) later.

---

## 4. Minimal Working Prototype (Python)

Below is a self‑contained script that:

1. Reads a `.md` file.  
2. Extracts nodes and edges using the DSL above.  
3. Generates a Graphviz diagram (`workflow.png`).  

```python
#!/usr/bin/env python3
"""
workflow_to_graphviz.py

Usage:
    python workflow_to_graphviz.py workflow.md output_name
"""

import sys
import re
from pathlib import Path
import graphviz

# ----------------------------------------------------------------------
# 1️⃣  Helper functions
# ----------------------------------------------------------------------
def read_markdown(md_path: Path) -> str:
    """Return the raw markdown text."""
    return md_path.read_text(encoding="utf-8")

def parse_workflow(md_text: str):
    """
    Very simple parser for the DSL described in the README.
    Returns:
        nodes: set(str)
        edges: list[(str, str)]
    """
    node_pattern = re.compile(r'^\s*\[(.+?)\]\s*(?:#.*)?$')
    edge_pattern = re.compile(r'^\s*\[(.+?)\]\s*->\s*\[(.+?)\]\s*(?:#.*)?$')

    nodes = set()
    edges = []

    for line in md_text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):   # skip empty lines & comments
            continue

        # Edge first (so we also capture nodes that appear only in edges)
        m_edge = edge_pattern.match(line)
        if m_edge:
            src, dst = m_edge.groups()
            nodes.update([src, dst])
            edges.append((src, dst))
            continue

        # Node definition
        m_node = node_pattern.match(line)
        if m_node:
            node = m_node.group(1).strip()
            nodes.add(node)

    return nodes, edges

# ----------------------------------------------------------------------
# 2️⃣  Graphviz rendering
# ----------------------------------------------------------------------
def render_graph(nodes, edges, out_name: str, fmt: str = "png"):
    """
    Create a Graphviz Digraph and write it to disk.
    """
    dot = graphviz.Digraph(comment="Workflow diagram", format=fmt)

    # Add nodes (you can customize shape, style, etc. here)
    for n in nodes:
        dot.node(n, n)   # label = name

    # Add edges
    for src, dst in edges:
        dot.edge(src, dst)

    # Render to file (creates out_name.<fmt> and a .dot source file)
    output_path = dot.render(filename=out_name, cleanup=True)
    print(f"✅ Diagram written to {output_path}")

# ----------------------------------------------------------------------
# 3️⃣  Main entry point
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: python workflow_to_graphviz.py <workflow.md> <output_name>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    out_name = sys.argv[2]

    if not md_path.is_file():
        print(f"❌ File not found: {md_path}")
        sys.exit(1)

    md_text = read_markdown(md_path)
    nodes, edges = parse_workflow(md_text)

    if not nodes:
        print("⚠️  No nodes detected – check your markdown syntax.")
        sys.exit(1)

    render_graph(nodes, edges, out_name)

if __name__ == "__main__":
    main()
```

### How to run it

```bash
# 1️⃣ Install dependencies (once)
pip install graphviz   # Python wrapper
# You also need the Graphviz binary:
#   Ubuntu: sudo apt-get install graphviz
#   macOS:  brew install graphviz

# 2️⃣ Save the script above as workflow_to_graphviz.py
# 3️⃣ Create a markdown file (e.g., workflow.md) using the DSL.
# 4️⃣ Generate the diagram:
python workflow_to_graphviz.py workflow.md my_workflow
# → produces my_workflow.png (and my_workflow.dot)
```

---

## 5. Turning the Script into an **AI Agent**

If you want the *agent* to **interpret natural‑language descriptions** (instead of the tiny DSL), you can add an LLM step that converts prose into the node/edge list. The overall flow becomes:

```
Markdown (free‑form)  -->  LLM Prompt (extract workflow)  -->  Structured JSON
          ^                                                    |
          |                                                    v
   (optional) user feedback loop <---  Agent validates  <--  Parser
```

### 5.1 Prompt Template (for GPT‑4/Claude)

```text
You are an assistant that extracts a directed workflow graph from the following markdown text.
Return a JSON object with two keys:
  "nodes":  list of unique node names (strings)
  "edges":  list of [source, target] pairs.

Only include steps that are explicitly mentioned as actions or decisions.
If the text contains ambiguous references, list them as separate nodes.

Markdown:
----
{INSERT_MARKDOWN_HERE}
----
```

### 5.2 Python glue code (using `openai` library)

```python
import openai, json, os

def extract_graph_with_llm(md_text: str) -> tuple[set[str], list[tuple[str, str]]]:
    prompt = f"""You are an assistant that extracts a directed workflow graph from the following markdown text.
Return a JSON object with two keys:
  "nodes": list of unique node names (strings)
  "edges": list of [source, target] pairs.

Markdown:
----
{md_text}
----
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    json_str = response.choices[0].message.content.strip()
    data = json.loads(json_str)

    nodes = set(data["nodes"])
    edges = [(src, dst) for src, dst in data["edges"]]
    return nodes, edges
```

Replace the `parse_workflow` call in the script with `extract_graph_with_llm(md_text)`.  
You’ll need an OpenAI API key (`export OPENAI_API_KEY=…`) and the `openai` Python package (`pip install openai`).

---

## 6. Extending the Agent (Optional Enhancements)

| Feature | How to add it |
|---------|---------------|
| **Node styling (colors, shapes)** | Extend the DSL: `[#ff0000] [Start]` → parse color; in Graphviz: `dot.node(name, style='filled', fillcolor='#ff0000')`. |
| **Sub‑graphs / clusters** | Use markdown headings (`## Subprocess A`) and group nodes under a `with dot.subgraph(name='cluster_A'):` block. |
| **Automatic layout tweaking** | Pass Graphviz engine arguments: `dot.attr(rankdir='LR')` for left‑to‑right flow. |
| **Web UI** | Wrap the script in a Flask/FastAPI endpoint that accepts a file upload and returns the PNG/SVG. |
| **Versioned diagrams** | Store the generated `.dot` source in a Git repo; each run creates a commit. |
| **Error handling & feedback** | After LLM extraction, validate that every edge references an existing node; if not, ask the LLM to “clarify missing node X”. |
| **Batch processing** | Loop over a directory of `.md` files, producing a diagram per file. |

---

## 7. Summary Checklist

| ✅ | Item |
|----|------|
| **✅ Install dependencies** | `pip install graphviz` + system Graphviz binary |
| **✅ Define a simple DSL** (or decide to use an LLM) |
| **✅ Write a parser** (`parse_workflow` or LLM‑based) |
| **✅ Generate Graphviz** (`graphviz.Digraph`) |
| **✅ Render to PNG/SVG** (`dot.render`) |
| **✅ (Optional) Wrap in an API** for on‑demand diagram generation |
| **✅ (Optional) Add AI inference** for free‑form markdown |

With these pieces in place you have a **complete AI‑agent pipeline** that can read a `.md` file, understand the workflow it describes, and output a professional Graphviz diagram ready for documentation, presentations, or further processing. Happy diagramming!
