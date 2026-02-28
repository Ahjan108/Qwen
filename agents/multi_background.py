#!/usr/bin/env python3
"""
Background agents: translate all atoms and metadata into all Chinese dialects and Japanese.
Uses cloud Qwen (DashScope). When ATOMS_SOURCE is set (path to phoenix_omega checkout),
runs full translation and writes to outputs/translations/. Otherwise runs a small demo.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def get_client():
    from openai import OpenAI
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("MODEL_SERVER", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    if not api_key:
        raise RuntimeError("Set QWEN_API_KEY or DASHSCOPE_API_KEY in GitHub Secrets")
    return OpenAI(api_key=api_key, base_url=base_url.rstrip("/"))


def run_translate_all_locales():
    """Translate all atoms and exercises to zh_CN, zh_TW, yue, ja_JP. Requires ATOMS_SOURCE."""
    script = Path(__file__).resolve().parent / "translate_atoms_all_locales.py"
    out_dir = OUTPUTS_DIR / "translations"
    out_dir.mkdir(parents=True, exist_ok=True)
    limit_ex = os.getenv("LIMIT_EXERCISES", "")
    limit_a = os.getenv("LIMIT_ATOMS", "")
    cmd = [sys.executable, str(script), "--out", str(out_dir)]
    if limit_ex:
        cmd.extend(["--limit-exercises", limit_ex])
    if limit_a:
        cmd.extend(["--limit-atoms", limit_a])
    r = subprocess.run(cmd, env=os.environ)
    return r.returncode == 0


def run_demo(client, model: str = "qwen-turbo"):
    """Fallback: one short chapter + run summary when no ATOMS_SOURCE."""
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
    path = OUTPUTS_DIR / "chapter.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"model": model, "content": content}, f, indent=2, ensure_ascii=False)
    with open(OUTPUTS_DIR / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump({"workflow": "qwen-agents", "mode": "demo"}, f, indent=2)
    return True


def main():
    atoms_source = os.getenv("ATOMS_SOURCE")
    source_path = Path(atoms_source).resolve() if atoms_source else None

    if source_path and source_path.is_dir():
        print("Running translation: all atoms and metadata → zh_CN, zh_TW, yue, ja_JP", flush=True)
        ok = run_translate_all_locales()
        if not ok:
            sys.exit(1)
        print("Translation done. Outputs:", list((OUTPUTS_DIR / "translations").rglob("*.json"))[:20], flush=True)
    else:
        print("ATOMS_SOURCE not set or missing; running demo only.", flush=True)
        client = get_client()
        run_demo(client, model=os.getenv("QWEN_MODEL", "qwen-turbo"))
    print("Agents finished.", flush=True)


if __name__ == "__main__":
    main()
