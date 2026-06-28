from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ----------------------------
# Read logs (from file or CI)
# ----------------------------
try:
    with open("build.log", "r") as f:
        logs = f.read()
except:
    logs = "No build.log found. Capture CI logs for debugging."

# ----------------------------
# Optional context files
# ----------------------------
try:
    with open("Dockerfile", "r") as f:
        dockerfile = f.read()
except:
    dockerfile = "No Dockerfile found."

# ----------------------------
# Prompt for Groq
# ----------------------------
prompt = f"""
You are a senior DevOps engineer.

Analyze this CI/CD failure.

--- Dockerfile ---
{dockerfile}

--- Build Logs ---
{logs}

Tasks:
1. Identify root cause
2. Explain in simple terms
3. Suggest fix
4. Provide improved Dockerfile if needed
5. Write a short failure summary for engineers
"""

# ----------------------------
# Call Groq API
# ----------------------------
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)

result = response.choices[0].message.content

# ----------------------------
# Save report
# ----------------------------
with open("failure_report.md", "w") as f:
    f.write(result)

print("✅ AI failure report generated: failure_report.md")