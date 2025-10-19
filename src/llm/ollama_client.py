# src/llm/ollama_client.py
import requests
import json
from config.settings import OLLAMA_API_URL, LLM_MODEL


def enrich_chunk(code_chunk: str) -> dict:
    """
    Generates a summary and keywords for a code chunk, returning a default on error.
    """
    if not code_chunk.strip():
        return {"summary": "", "keywords": ""}

    prompt = f"""
    Analyze the following code chunk and provide a one-sentence summary and a comma-separated list of keywords.
    Respond with a single JSON object with two keys: "summary" and "keywords".

    Code:
    ```
    {code_chunk}
    ```

    JSON Response:
    """

    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)

        # Check for HTTP errors like 500 first.
        if response.status_code >= 400:
            if response.status_code == 500:
                print("\n--- Ollama Server Error ---")
                print("The Ollama server ran into an internal error (500).")
                print(
                    "This is often caused by low RAM/VRAM. Try closing other resource-intensive applications."
                )
                print("---------------------------\n")
            else:
                print(f"[Ollama HTTP Error {response.status_code}: {response.text}]")

            # Immediately return the default value on any HTTP error.
            return {"summary": "", "keywords": ""}

        # --- Only process a successful response ---
        json_data = response.json()
        content_string = json_data.get("message", {}).get("content", "{}")
        enriched_data = json.loads(content_string)

        return {
            "summary": enriched_data.get("summary", ""),
            "keywords": enriched_data.get("keywords", ""),
        }

    except requests.exceptions.RequestException as e:
        print(
            f"\n[Network Error]: Could not connect to Ollama at {OLLAMA_API_URL}. Is the server running?"
        )
        return {"summary": "", "keywords": ""}
    except json.JSONDecodeError as e:
        print(f"\n[JSON Decode Error]: Failed to parse response from Ollama.")
        return {"summary": "", "keywords": ""}
