import json
from config.settings import MODEL_NAME, TEMPERATURE
from services.mistral_client import get_mistral_client


def _parse_model_json(raw_output: str):
    """
    Parse JSON from model output.
    Handles cases where the LLM wraps content in ```json fences.
    """
    if not raw_output or not raw_output.strip():
        raise ValueError("Empty response from model")

    cleaned = raw_output.strip()

    # Strip surrounding fences like ```json ... ```
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse model response as JSON: {exc.msg}") from exc


def analyze_resume(text, techstack, index, prompt_template):
    client = get_mistral_client(index)

    prompt = prompt_template \
        .replace("{{RESUME_TEXT}}", text) \
        .replace("{{EXPECTED_TECHSTACK}}", techstack)

    response = client.chat.complete(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE
    )

    raw_output = response.choices[0].message.content
    try:
        return _parse_model_json(raw_output)
    except Exception as exc:
        return {
            "error": str(exc),
            "raw_output": raw_output
        }
