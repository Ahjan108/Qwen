# Qwen Background Agents

Python agents that run on **GitHub Actions** using **cloud Qwen APIs** (DashScope or other OpenAI-compatible endpoints). No local Qwen required.

## How it works

- **Workflow:** `.github/workflows/qwen-agents.yml` runs on `workflow_dispatch` (manual) and/or a schedule (e.g. every 6 hours).
- **Runner:** Ubuntu on GitHub-hosted runners; installs `openai` and runs `agents/multi_background.py`.
- **API:** Script uses `QWEN_API_KEY` (or `DASHSCOPE_API_KEY`) and `MODEL_SERVER` (OpenAI-compatible base URL). Default server: DashScope compatible-mode (China). Use repo variable `MODEL_SERVER` to point to another region (e.g. `https://dashscope-us.aliyuncs.com/compatible-mode/v1`).
- **Outputs:** Agents write JSON (and any other files) under `outputs/`. The workflow uploads `outputs/*.json` as artifact `agent-results`.

## Setup

1. **GitHub Secrets** (repo Settings → Secrets and variables → Actions):
   - `DASHSCOPE_API_KEY` — your DashScope (Alibaba Cloud) API key.

2. **Optional:** Repo variable `MODEL_SERVER` to override the API base URL (e.g. US or Singapore DashScope).

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
