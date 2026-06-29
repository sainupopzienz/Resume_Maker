from openai import OpenAI
import json
import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ------------------------
# LOAD BUILD LOG
# ------------------------
try:
    with open("build.log", "r") as f:
        build_logs = f.read()
except:
    build_logs = None

# ------------------------
# LOAD TRIVY SCAN
# ------------------------
try:
    with open("scan.json", "r") as f:
        scan_data = json.load(f)
except:
    scan_data = None

# ------------------------
# SMART PROMPT (IMPORTANT PART)
# ------------------------
prompt = f"""
You are a Senior DevOps + DevSecOps engineer.

You MUST analyze BOTH sections if available.

RULES:
1. Always prioritize BUILD FAILURE first if present
2. Then analyze SECURITY (Trivy CVEs)
3. If both exist, merge into a single structured report
4. Provide actionable fixes for each issue

---

BUILD FAILURE LOGS:
{build_logs if build_logs else "No build failure detected"}

---

TRIVY SECURITY SCAN:
{json.dumps(scan_data, indent=2) if scan_data else "No security issues detected"}

---

OUTPUT FORMAT:

## 🚨 Primary Issue (Build / CI Failure)
- Root cause
- Fix
- Suggested Dockerfile/code change

## ⚠️ Security Issues (CVEs)
- List HIGH/CRITICAL issues
- Risk explanation
- Fix (base image / dependency upgrade)

## 🧠 Final Recommendation
- What to fix first
- What to improve long-term
"""

# ------------------------
# CALL GROQ
# ------------------------
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)

result = response.choices[0].message.content

# ------------------------
# SAVE OUTPUT
# ------------------------
with open("auto_healing_report.md", "w") as f:
    f.write(result)

print("✅ Auto-healing report generated successfully")
