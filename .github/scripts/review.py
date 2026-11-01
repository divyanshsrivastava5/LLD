import os
import glob
import time
import logging
import subprocess
from collections.abc import Sequence
from google import genai
from google.genai.errors import APIError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODELS: tuple[str, ...] = (
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-3.8-flash",
)
RULES_FILE = "agents/solid_agent.md"


def get_target_code() -> tuple[str | None, str]:
    target_filter = ":(exclude).github/*"

    # Try diff against previous commit
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD", "--", "*.py", target_filter],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if diff:
            return "diff", diff
    except Exception:
        pass

    # Fallback to reading all current Python files
    py_files = [
        f for f in glob.glob("**/*.py", recursive=True)
        if not f.startswith(".github") and not f.startswith(".venv") and not f.startswith("venv")
    ]
    if not py_files:
        return None, ""

    combined = []
    for path in py_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                combined.append(f"### File: {path}\n```python\n{f.read()}\n```")
        except Exception:
            continue

    return "full_files", "\n\n".join(combined)


def call_gemini(client: genai.Client, prompt: str) -> tuple[str, str]:
    for model in MODELS:
        for attempt in range(2):
            try:
                logger.info("Evaluating with model: %s...", model)
                res = client.models.generate_content(model=model, contents=prompt)
                if res.text:
                    return res.text, model
            except APIError as e:
                if getattr(e, "code", None) in {429, 503}:
                    time.sleep((attempt + 1) * 3)
                else:
                    break
            except Exception:
                break
    raise RuntimeError("Unable to complete review with available Gemini models.")


def run():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is not set.")
        return

    content_type, code = get_target_code()
    if not code:
        logger.info("No Python changes found to review.")
        return

    rules = ""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules = f.read()

    fence = "```"
    prompt = (
        f"{rules}\n\nReview the following Python code based on the instructions above:\n\n"
        f"{fence}{'diff' if content_type == 'diff' else 'python'}\n{code}\n{fence}"
    )

    try:
        client = genai.Client(api_key=api_key)
        review, model_used = call_gemini(client, prompt)

        print("\n" + "=" * 50)
        print(f"AI INTERVIEW REVIEW ({model_used})")
        print("=" * 50 + "\n")
        print(review)

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(f"## 🤖 LLD Interview Review (`{model_used}`)\n\n{review}\n")

    except Exception as e:
        logger.error("Review failed: %s", e)


if __name__ == "__main__":
    run()