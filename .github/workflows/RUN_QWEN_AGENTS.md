# How to run Qwen Background Agents and get results

The workflow runs on **GitHub.com** in the repo that contains it — that’s **Ahjan108/Qwen** (this repo’s `origin`).

---

## Step 0: Push the workflow (one-time)

If you just added the workflow on your machine, push it so GitHub has the file:

```bash
cd Qwen   # or path to your Qwen clone
git add .github/workflows/qwen-agents.yml agents/
git status   # should show the new/changed files
git commit -m "Add Qwen background agents workflow"
git push origin main
```

(Use your branch name if it’s not `main`.)

---

## Step 1: Run the workflow

1. Open **https://github.com/Ahjan108/Qwen** in your browser.
2. Click the **Actions** tab (top bar).
3. In the left sidebar, click **“Qwen Background Agents”**.
4. On the right, click the **“Run workflow”** dropdown (grey button).
5. Click the green **“Run workflow”** button.
6. Wait. A new run appears at the top; it goes yellow (running) then green (done) or red (failed). Click that run to open it.

---

## Step 2: Get the results

1. You’re on the run page (e.g. `https://github.com/Ahjan108/Qwen/actions/runs/...`).
2. Scroll to the **bottom** of the page.
3. Under **Artifacts**, you’ll see **agent-results**.
4. Click **agent-results** to download a ZIP file.
5. Unzip it: inside is the **outputs/** folder with the JSON files (e.g. `chapter.json`, `run_summary.json`).

---

## Summary

| Where        | What |
|-------------|------|
| **GitHub repo** | https://github.com/Ahjan108/Qwen — workflow runs here. |
| **Run workflow** | Actions → Qwen Background Agents → “Run workflow” dropdown → Run workflow. |
| **Results**      | Open the run → scroll to Artifacts → download **agent-results** (ZIP of `outputs/`). |

The secret **DASHSCOPE_API_KEY** is used by the workflow on GitHub; your laptop never runs the agents.
