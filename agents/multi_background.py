#!/usr/bin/env python3
"""
Background agents that run on GitHub Actions using cloud Qwen APIs (DashScope, etc.).
Uses MODEL_SERVER + QWEN_API_KEY; no local Qwen. Writes results to outputs/*.json.
"""
import json
import os
from pathlib import Path

# Ensure outputs dir exists
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def get_client():
    """OpenAI-compatible client for cloud Qwen (DashScope compatible-mode or other)."""
    from openai import OpenAI
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("MODEL_SERVER", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    if not api_key:
        raise RuntimeError("Set QWEN_API_KEY or DASHSCOPE_API_KEY in GitHub Secrets")
    return OpenAI(api_key=api_key, base_url=base_url.rstrip("/"))


def run_audiobook_agent(client, model: str = "qwen-turbo"):
    """Example: generate one audiobook chapter via cloud Qwen. Save to outputs/chapter.json."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a calm self-help audiobook narrator. Write in second person, present tense. Output only the prose, no meta."},
            {"role": "user", "content": "Generate one short audiobook chapter (2–3 paragraphs) about pausing to notice the breath when stressed."},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    content = response.choices[0].message.content if response.choices else ""
    out = {"model": model, "content": content, "usage": getattr(response, "usage", None)}
    path = OUTPUTS_DIR / "chapter.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return path


def run_summary_agent(client, model: str = "qwen-turbo"):
    """Example: produce a run summary so artifact upload always has at least one file."""
    summary = {
        "workflow": "qwen-agents",
        "artifacts": [p.name for p in OUTPUTS_DIR.glob("*.json")],
    }
    path = OUTPUTS_DIR / "run_summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return path


def main():
    client = get_client()
    model = os.getenv("QWEN_MODEL", "qwen-turbo")
    run_audiobook_agent(client, model=model)
    run_summary_agent(client, model=model)
    print("Agents finished. Outputs:", list(OUTPUTS_DIR.glob("*.json")))


if __name__ == "__main__":
    main()
