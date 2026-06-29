# 🤖 AI-Powered DevSecOps CI/CD Pipeline

> A production-grade CI/CD pipeline with **AI auto-healing** — automatically analyzes Docker build failures and Trivy security scans using LLMs, generating actionable fix reports.

---

## 🏗️ Architecture Overview

```
Code Push (GitHub)
       ↓
┌─────────────────────────────────────────┐
│              CI JOB                     │
│                                         │
│  1. 🐳 Docker Build → build.log         │
│  2. 🔍 Trivy Scan   → scan.json         │
│  3. 🤖 AI Analysis  → auto_healing.md   │
│  4. 📦 Upload Artifacts                 │
└─────────────────────────────────────────┘
       ↓ (only if CI passes + main branch)
┌─────────────────────────────────────────┐
│              CD JOB                     │
│                                         │
│  5. 🚀 Deploy to Render                 │
└─────────────────────────────────────────┘
```

---

## ⚙️ How It Works

### Step 1 — Docker Build
```bash
docker build -t resume-app . 2>&1 | tee build.log
docker save resume-app -o resume-app.tar
```
- Builds the Docker image
- Captures **all output** (success or failure) into `build.log`
- Saves image as `.tar` so Trivy can scan it without Docker daemon issues

---

### Step 2 — Trivy Security Scan
```bash
trivy image --input resume-app.tar --format json --output scan.json
```
- Scans for **CRITICAL and HIGH CVEs**
- Outputs results to `scan.json`
- Pipeline does **NOT fail** on CVEs (`exit-code: 0`) — AI handles analysis

---

### Step 3 — AI Analysis 🤖

```
build.log  ──┐
              ├──▶ Python Script ──▶ OpenRouter API ──▶ LLM ──▶ auto_healing_report.md
scan.json  ──┘
```

The Python script (`scripts/analyze_failure.py`):
1. Reads `build.log` — truncated to 3,000 chars
2. Reads `scan.json` — extracts top 20 CRITICAL/HIGH CVEs only
3. Sends both to `openrouter/free` (auto-selects best free LLM)
4. AI generates a structured markdown report with root cause + fixes

---

### Step 4 — Artifact Upload
Both the AI report and raw scan results are uploaded as GitHub Actions artifacts, retained for **30 days**.

---

### Step 5 — Deploy to Render
Only triggers when:
- ✅ CI job fully passed
- ✅ Branch is `main`

---

## 📁 Project Structure

```
Resume_Maker/
│
├── Dockerfile
├── resume-builder.html
│
├── scripts/
│   └── analyze_failure.py      ← AI analysis script
│
└── .github/
    └── workflows/
        └── cicd.yml            ← Full pipeline
```

---

## 🔐 GitHub Secrets Required

`Repo → Settings → Secrets and variables → Actions → New Secret`

> ⚠️ Make sure to name it `OPENROUTER_API_KEY` exactly — not `GROQ_API_KEY`

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | OpenRouter API key |
| `RENDER_DEPLOY_HOOK_URL` | `https://api.render.com/deploy/...` | Render deploy webhook |

---

## 🤖 AI Analysis Script

Uses **OpenRouter free router** with smart model fallback:

```python
FREE_MODELS = [
    "openrouter/free",                          # Auto-picks best free model
    "meta-llama/llama-3.3-70b-instruct:free",  # Fallback 1
    "nvidia/nemotron-nano-12b-v2-vl:free",     # Fallback 2
]
```

**Smart truncation** prevents token limit errors:
- Build log → max 3,000 characters
- Trivy scan → top 20 CVEs only (sorted CRITICAL first)

---

## 📊 AI Report Output Format

```markdown
## 🚨 Primary Issue (Build / CI Failure)
- Root cause
- Fix
- Suggested Dockerfile change

## ⚠️ Security Issues (CVEs)
- List of CRITICAL/HIGH CVEs
- Risk explanation
- Fix (base image / dependency upgrade)

## 🧠 Final Recommendation
- What to fix first
- Long-term improvements
```

---

## 🧪 How to Test — Simulate Errors

### ❌ Test 1 — Wrong COPY Filename (Most Common Mistake)

Change your `Dockerfile`:

```dockerfile
FROM nginx:alpine

# ❌ Wrong filename — your actual file is resume-builder.html
COPY nonexistent-file.html /usr/share/nginx/html/index.html
```

**What happens:**
```
Docker build FAILS ❌
build.log: "COPY failed: file not found in build context"
AI reads build.log → explains root cause → suggests fix
CD job SKIPS
```

**AI Report will say:**
> The COPY instruction references `nonexistent-file.html` which does not exist
> in the build context. Fix: use the correct filename `resume-builder.html`.

**Fix:**
```dockerfile
# ✅ Correct
COPY resume-builder.html /usr/share/nginx/html/index.html
```

---

### ❌ Test 2 — Security CVEs (Old Base Image)

```dockerfile
# ❌ Old image with known CVEs
FROM nginx:1.14.0

COPY resume-builder.html /usr/share/nginx/html/index.html
```

**What happens:**
```
Docker build succeeds ✅
Trivy finds 50+ CRITICAL/HIGH CVEs ⚠️
AI reads top 20 CVEs → explains each → recommends fix
CD deploys (exit-code: 0 means pipeline continues)
```

**AI Report will say:**
> Multiple CRITICAL CVEs found in nginx:1.14.0 including OpenSSL vulnerabilities.
> Fix: Upgrade base image to `nginx:alpine` — reduces attack surface significantly.

**Fix:**
```dockerfile
# ✅ Correct
FROM nginx:alpine
```

---

### ❌ Test 3 — Dockerfile Syntax Error

```dockerfile
FROM nginx:alpine

# ❌ Unclosed quote — syntax error
RUN echo "hello

COPY resume-builder.html /usr/share/nginx/html/index.html
```

**What happens:**
```
Docker build FAILS immediately ❌
AI explains the unclosed string literal
CD job SKIPS
```

---

### ❌ Test 4 — Non-existent Base Image

```dockerfile
# ❌ This tag does not exist
FROM nginx:this-tag-does-not-exist

COPY resume-builder.html /usr/share/nginx/html/index.html
```

**What happens:**
```
Docker pull FAILS ❌
build.log: "manifest unknown: manifest unknown"
AI explains the image tag doesn't exist on Docker Hub
```

---

## 🔄 Pipeline Flow by Scenario

| Failure Point | Pipeline Stops? | AI Report? | Deploy? |
|---------------|----------------|------------|---------|
| Docker build fails | CI fails ❌ | ✅ Yes | ❌ No |
| Trivy finds CVEs | ❌ No | ✅ Yes | ✅ Yes |
| AI script crashes | ❌ No | ❌ No | ✅ Yes |
| API key missing | CI fails ❌ | ❌ No | ❌ No |
| Render deploy fails | CD fails ❌ | ✅ Yes | ❌ Failed |
| Everything passes | ❌ No | ✅ Yes | ✅ Yes |

---

## 📦 Viewing the AI Report

After any pipeline run:

```
GitHub Repo
  → Actions tab
    → Your workflow run
      → Scroll to bottom
        → Artifacts section
          → auto-healing-report    ← Download AI analysis
          → trivy-scan-results     ← Raw CVE JSON data
```

---

## 🔥 Key Features

| Feature | Detail |
|---------|--------|
| 🤖 AI Auto-healing | LLM analyzes failures and generates fix reports |
| 🔐 Security Scanning | Trivy scans for CRITICAL/HIGH CVEs |
| 📦 Artifact Storage | Reports saved for 30 days |
| 💰 Zero Cost | Uses OpenRouter free models |
| 🔄 Smart Fallback | 3 model fallbacks if one is unavailable |
| 🚀 Auto Deploy | Deploys to Render on main branch only |
| 📊 Token Safe | Smart truncation prevents context overflow |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| GitHub Actions | CI/CD orchestration |
| Docker | Container build & packaging |
| Trivy v0.36.0 | CVE security scanning |
| OpenRouter | Free LLM API gateway |
| `openrouter/free` | Auto-selects best free model |
| Python + OpenAI SDK | AI integration layer |
| Render | Production deployment |

---

## 🐛 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `No such image: resume-app` | Trivy can't see Docker image | Use `docker save` + `input:` param |
| `No module named openai` | pip install ran after failure | Move pip install to top of pipeline |
| `402 insufficient credits` | No OpenRouter balance | Use `openrouter/free` model |
| `context length exceeded` | scan.json too large (200k+ tokens) | Truncate to top 20 CVEs in script |
| `Missing credentials` | Wrong env var name | Set `OPENROUTER_API_KEY` in GitHub Secrets |
| `COPY failed: file not found` | Wrong filename in Dockerfile | Match exact filename in your repo |
| `404 model not found` | Free model removed | Use `openrouter/free` — auto-updates |

---

## 🎯 One-liner for Resume / Interviews

> *"Built an AI-powered DevSecOps CI/CD pipeline that automatically analyzes Docker build failures and Trivy CVE scans using LLMs via OpenRouter, generating actionable fix reports as GitHub Actions artifacts — zero cost, auto-deployed to Render."*

---

*Built with ❤️ — AI-assisted, human-debugged, production-ready.*
