import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def explain_code(code):
    """Explain repository source code using the local Ollama model."""

    if not code or not code.strip():
        return "No source code was available to explain."

    # Limit input size to reduce processing time.
    code = code[:8000]

    prompt = f"""
You are a helpful programming tutor.
Explain this GitHub project's source code in simple English.
Include:
1. Project purpose
2. Important files and functions
3. Technologies used
4. How the project works

Keep the explanation concise and beginner-friendly.

SOURCE CODE:
{code}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 350
                }
            },
            timeout=(10, 240)
        )

        response.raise_for_status()
        data = response.json()

        explanation = data.get("response", "").strip()

        if not explanation:
            raise RuntimeError("Ollama returned an empty explanation.")

        return explanation

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "Ollama took too long. Try a smaller repository."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to Ollama: {exc}"
        ) from exc
