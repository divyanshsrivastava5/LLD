import json
import os
import subprocess
import urllib.request


def get_git_diff():
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD", "--", "*.py"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return diff.strip()
    except Exception:
        try:
            diff = subprocess.check_output(
                ["git", "diff", "4b825dc642cb6eb9a060e54bf8d69288fbee4904", "HEAD", "--", "*.py"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            return diff.strip()
        except Exception:
            return ""


def run_review():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not found.")
        return

    diff = get_git_diff()
    if not diff:
        print("No Python (.py) file changes found to review.")
        return

    rules_path = "agents/solid_agent.md"
    rules = ""
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = f.read()

    fence = "```"
    prompt = (
        "System Rules & Persona:\n"
        + rules
        + "\n\nReview the following git diff based strictly on your rules:\n\n"
        + fence + "diff\n"
        + diff + "\n"
        + fence
    )

    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=){api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            review_text = res_data["candidates"][0]["content"]["parts"][0]["text"]

            print("\n" + "=" * 50)
            print("AI CODE REVIEW RESULTS")
            print("=" * 50 + "\n")
            print(review_text)

            step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if step_summary:
                with open(step_summary, "a", encoding="utf-8") as f:
                    f.write(f"## 🤖 AI Code Review\n\n{review_text}\n")
    except Exception as e:
        print(f"Error during Gemini review: {e}")


if __name__ == "__main__":
    run_review()