#!/usr/bin/env python3
"""
Translate all atoms and metadata into all Chinese dialects and Japanese (cloud Qwen).
Reads from ATOMS_SOURCE (path to phoenix_omega repo root); writes to --out (default outputs/translations).
Used by multi_background.py when this repo's workflow checkouts phoenix_omega.
"""
import json
import os
import sys
from pathlib import Path

# When run from Qwen workflow, ATOMS_SOURCE is set to the checked-out phoenix_omega path.
SOURCE_ROOT = Path(os.environ.get("ATOMS_SOURCE", ".")).resolve()
EXERCISES_V4 = SOURCE_ROOT / "SOURCE_OF_TRUTH" / "exercises_v4"
ATOMS_ROOT = SOURCE_ROOT / "atoms"

# Output: default to outputs/translations under repo root (Qwen)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT = REPO_ROOT / "outputs" / "translations"

MODEL_SERVER = os.environ.get("MODEL_SERVER", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL = os.environ.get("QWEN_MODEL", "qwen-turbo")

LOCALES = {
    "zh_CN": "简体中文（中国大陆），仅输出译文，无解释。",
    "zh_TW": "繁體中文（台灣/香港書面），仅输出译文，无解释。",
    "yue": "粤语（廣東話，口语化书面），仅输出译文，无解释。",
    "ja_JP": "自然な日本語で。説明は不要、訳文のみ。",
}

TRANSLATE_SYSTEM = """You are a precise translator for therapeutic and self-help content.
Preserve 100% of the meaning. Use second person and present tense where the source does.
Output only the translated text. No commentary, no explanation."""


def get_client():
    from openai import OpenAI
    key = os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError("Set QWEN_API_KEY or DASHSCOPE_API_KEY")
    return OpenAI(api_key=key, base_url=MODEL_SERVER.rstrip("/"))


def translate_text(client, text: str, locale: str) -> str:
    if not text or not text.strip():
        return text
    instruction = LOCALES[locale]
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": TRANSLATE_SYSTEM},
            {"role": "user", "content": f"Translate the following into {instruction}\n\n---\n\n{text}"},
        ],
        temperature=0.2,
        max_tokens=4000,
    )
    return (r.choices[0].message.content or "").strip() if r.choices else ""


def load_exercises():
    try:
        import yaml
    except ImportError:
        return []
    seen = set()
    out = []
    for base in ("candidate/_stubs", "approved"):
        if not (EXERCISES_V4 / base).exists():
            continue
        for p in sorted((EXERCISES_V4 / base).rglob("*.yaml")):
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not data or not isinstance(data.get("content"), dict):
                continue
            eid = data.get("id") or p.stem
            if eid in seen:
                continue
            seen.add(eid)
            data["_path"] = str(p)
            out.append(data)
    return out


def load_atoms(limit=None):
    out = []
    if not ATOMS_ROOT.exists():
        return out
    for p in sorted(ATOMS_ROOT.rglob("CANONICAL.txt")):
        if limit is not None and len(out) >= limit:
            break
        try:
            text = p.read_text(encoding="utf-8").strip()
        except Exception:
            continue
        parts = p.relative_to(ATOMS_ROOT).parts
        persona, topic, engine = (parts[0], parts[1], parts[2]) if len(parts) >= 4 else ("", "", "")
        out.append({
            "id": f"{persona}/{topic}/{engine}",
            "persona": persona, "topic": topic, "engine": engine,
            "body": text, "_path": str(p),
        })
    return out


def translate_exercise(client, ex, locale):
    content = ex.get("content") or {}
    translated = {}
    for key in ("intro", "guided_practice", "aha_noticing", "integration"):
        translated[key] = translate_text(client, (content.get(key) or "").strip(), locale) if content.get(key) else ""
    return {
        "id": ex.get("id"), "exercise_type": ex.get("exercise_type"),
        "metadata": ex.get("metadata"), "content": translated, "approval": ex.get("approval"),
    }


def translate_atom(client, atom, locale):
    return {
        "id": atom["id"], "persona": atom["persona"], "topic": atom["topic"], "engine": atom["engine"],
        "body": translate_text(client, atom["body"], locale),
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-exercises", type=int, default=None)
    ap.add_argument("--limit-atoms", type=int, default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUTPUT))
    args = ap.parse_args()

    out_root = Path(args.out)
    locales = list(LOCALES.keys())
    client = get_client()
    exercises = load_exercises()
    atoms = load_atoms(limit=args.limit_atoms)
    if args.limit_exercises is not None:
        exercises = exercises[: args.limit_exercises]

    manifest = {"exercises": len(exercises), "atoms": len(atoms), "locales": locales, "files": []}

    for locale in locales:
        (out_root / locale / "exercises").mkdir(parents=True, exist_ok=True)
        (out_root / locale / "atoms").mkdir(parents=True, exist_ok=True)
        for ex in exercises:
            ex_id = ex.get("id") or "unknown"
            try:
                out_ex = translate_exercise(client, ex, locale)
                path = out_root / locale / "exercises" / f"{ex_id}.json"
                path.write_text(json.dumps(out_ex, indent=2, ensure_ascii=False), encoding="utf-8")
                manifest["files"].append(str(path.relative_to(out_root)))
            except Exception as e:
                print(f"  [{locale}] exercise {ex_id}: {e}", file=sys.stderr)
        for atom in atoms:
            aid = atom["id"].replace("/", "_")
            try:
                out_atom = translate_atom(client, atom, locale)
                path = out_root / locale / "atoms" / f"{aid}.json"
                path.write_text(json.dumps(out_atom, indent=2, ensure_ascii=False), encoding="utf-8")
                manifest["files"].append(str(path.relative_to(out_root)))
            except Exception as e:
                print(f"  [{locale}] atom {aid}: {e}", file=sys.stderr)

    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Done. Manifest:", out_root / "manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
