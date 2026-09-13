from main import (
    build_flow_diagram,
    generate_dot_from_markdown,
    generate_response,
    prepare_prompt_for_groq,
    render_dot_to_svg,
)


def test_generate_response_returns_text():
    answer = generate_response("Explain how a login flow works")
    assert isinstance(answer, str)
    assert len(answer) > 20


def test_prepare_prompt_for_groq_trims_large_input():
    long_prompt = "This is a long prompt. " * 200
    prepared = prepare_prompt_for_groq(long_prompt)
    assert len(prepared) <= 4000
    assert prepared.endswith("...")


def test_generate_dot_from_markdown_creates_graph_code():
    markdown = "# Project Launch\n\n## Step 1: Plan\n\n## Step 2: Build\n\n## Step 3: Validate"
    dot = generate_dot_from_markdown(markdown)
    assert "digraph" in dot.lower()
    assert "Project Launch" in dot
    assert "Plan" in dot and "Validate" in dot


def test_render_dot_to_svg_creates_svg():
    dot = build_flow_diagram("Plan a project launch")
    svg = render_dot_to_svg(dot)
    assert "<svg" in svg.lower()
    assert "digraph" not in svg.lower()


def test_build_flow_diagram_returns_dot_source():
    dot = build_flow_diagram("Plan a project launch")
    assert "digraph" in dot.lower()
    assert "Start" in dot or "User" in dot
