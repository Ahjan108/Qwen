# Qwen Background Agents

Python agents that run on **GitHub Actions** using **cloud Qwen APIs** (DashScope or other OpenAI-compatible endpoints). No local Qwen required.

## How it works

- **Workflow:** `.github/workflows/qwen-agents.yml` runs on `workflow_dispatch` (manual) and/or a schedule (e.g. every 6 hours).
- **Translation:** When `ATOMS_SOURCE` is set (path to phoenix_omega checkout), the agent runs `translate_atoms_all_locales.py`: reads exercises from `SOURCE_OF_TRUTH/exercises_v4` and atoms from `atoms/**/CANONICAL.txt`, translates each into zh_CN, zh_TW, yue, ja_JP, and writes `outputs/translations/{locale}/exercises/` and `outputs/translations/{locale}/atoms/`.
- **Fallback:** If phoenix_omega is not checked out, the agent runs a small demo (one chapter + summary).
- **API:** Script uses `QWEN_API_KEY` (or `DASHSCOPE_API_KEY`) and `MODEL_SERVER`. Default: DashScope compatible-mode (China).
- **Outputs:** Workflow uploads `outputs/` as artifact `agent-results`.

## Setup

1. **GitHub Secrets** (repo Settings → Secrets and variables → Actions):
   - **`DASHSCOPE_API_KEY`** — required. Your DashScope (Alibaba Cloud) API key.
   - **`PHOENIX_OMEGA_TOKEN`** — optional. A PAT with read access to the phoenix_omega repo (e.g. Ahjan108/phoenix_omega). If set, the workflow checkouts phoenix_omega and runs the full translation; if not set, the agent runs a short demo only.

2. **Optional:** Repo variable `PHOENIX_OMEGA_REPO` to override the atoms repo (default `Ahjan108/phoenix_omega`). Repo variable `MODEL_SERVER` to override the API base URL.

## Run

- **Manual:** Actions → “Qwen Background Agents” → “Run workflow”.
- **Logs:** Open the run and watch the “Run Agents” step.
- **Results:** In the same run, open the “agent-results” artifact and download the ZIP (contains `outputs/*.json`).

## Add your own agents

Edit `multi_background.py`:

- Use `get_client()` to get the OpenAI-compatible client.
- Add new functions that call `client.chat.completions.create(...)` and write results under `OUTPUTS_DIR` (e.g. `outputs/audiobook_chapter_1.json`).
- Call them from `main()`.

Example for translations or TTS scripts: same pattern — call the API, write JSON (or text) into `outputs/`, then download from the workflow artifact.
