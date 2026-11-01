from collections.abc import Sequence
import glob
import logging
import os
from pathlib import Path
import subprocess
import time
from google import genai, APIError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Module-level immutable defaults (adheres to PEP 8 & OCP recommendations)
DEFAULT_MODELS: tuple[str, ...] = (
    "gemini-3.8-flash",
    "gemini-3.8-flash-lite",
)
DEFAULT_RULES_PATH = Path("agents/solid_agent.md")
TARGET_FILTER = ":(exclude).github/*"


def get_target_code() -> tuple[str | None, str]:
    """Retrieves git diff or scans repository Python files, ignoring metadata and virtual environments."""
    for base_ref in ["HEAD~1", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]:
        try:
            diff = subprocess.check_output(
                ["git", "diff", base_ref, "HEAD", "--", "*.py", TARGET_FILTER],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            if diff:
                return "diff", diff
        except Exception:
            continue

    # Fallback to reading all Python files
    py_files = [
        f for f in glob.glob("**/*.py", recursive=True)
        if not f.startswith((".github", ".venv", "venv"))
    ]
    if not py_files:
        return None, ""

    combined = []
    for filepath in py_files:
        try:
            content = Path(filepath).read_text(encoding="utf-8")
            combined.append(f"### File: {filepath}\n```python\n{content}\n```")
        except Exception as e:
            logger.warning("Could not read %s: %s", filepath, e)
            continue

    return "full_files", "\n\n".join(combined)


def call_gemini_with_fallback(
    client: genai.Client,
    prompt: str,
    models: Sequence[str] = DEFAULT_MODELS,
    max_retries: int = 2,
    base_backoff_sec: int = 3,
) -> tuple[str, str]:
    """Generates a review using candidate models in sequence with exponential backoff for high demand."""
    for model_name in models:
        for attempt in range(max_retries):
            try:
                logger.info("Evaluating review with model: %s...", model_name)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response.text:
                    return response.text, model_name
                raise ValueError(f"Empty response returned from model {model_name}")

            except APIError as e:
                # Retry on 503 (high demand) or 429 (rate limits)
                if getattr(e, "code", None) in {429, 503}:
                    wait_time = (attempt + 1) * base_backoff_sec
                    logger.warning(
                        "Model %s busy (%s). Retrying in %ds...",
                        model_name,
                        e.message,
                        wait_time,
                    )
                    time.sleep(wait_time)
                else:
                    logger.warning("Skipping model %s due to error: %s", model_name, e.message)
                    break
            except Exception as e:
                logger.warning("Unexpected error with model %s: %s", model_name, e)
                break

    raise RuntimeError("All candidate Gemini models were unavailable or exhausted.")


def run_review(rules_path: Path = DEFAULT_RULES_PATH) -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not configured.")
        return

    content_type, code_content = get_target_code()
    if not code_content:
        logger.info("No Python code or changes found to review.")
        return

    rules = ""
    if rules_path.exists():
        rules = rules_path.read_text(encoding="utf-8")

    fence = "```"
    prompt = (
        f"{rules}\n\n"
        f"Review the following Python code based on the instructions above:\n\n"
        f"{fence}{'diff' if content_type == 'diff' else 'python'}\n"
        f"{code_content}\n"
        f"{fence}"
    )

    try:
        client = genai.Client(api_key=api_key)
        review_text, model_used = call_gemini_with_fallback(client, prompt)

        print("\n" + "=" * 50)
        print(f"AI INTERVIEW REVIEW ({model_used})")
        print("=" * 50 + "\n")
        print(review_text)

        step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if step_summary:
            with open(step_summary, "a", encoding="utf-8") as f:
                f.write(f"## 🤖 LLD Interview Review (`{model_used}`)\n\n{review_text}\n")

    except Exception as e:
        logger.error("Review run failed: %s", e)


if __name__ == "__main__":
    run_review()