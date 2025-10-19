# src/llm/ollama_client.py
import sys
import requests
import json
from config.settings import OLLAMA_API_URL, LLM_MODEL


def stream_ollama_response(prompt: str) -> str:
    """
    Send a streaming request to Ollama and capture the full response text.
    """
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }
    response = requests.post(OLLAMA_API_URL, json=payload, stream=True)

    if response.status_code == 200:
        collected_text = []
        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line)
                    if "message" in json_data and "content" in json_data["message"]:
                        chunk = json_data["message"]["content"]
                        collected_text.append(chunk)
                except json.JSONDecodeError:
                    print(f"\n[Non-JSON line received:] {line}")
        return "".join(collected_text).strip()
    else:
        return f"[Ollama error {response.status_code}: {response.text}]"


def enrich_chunk(code_chunk: str) -> dict:
    """
    Generates a summary and keywords for a code chunk in a single LLM call.
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

    # Using a non-streaming request here is often simpler for JSON parsing
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",  # Request JSON output
        "stream": False,  # We want the full JSON object at once
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        # Check for HTTP errors like 500
        if response.status_code >= 400:
            if response.status_code == 500:
                print("\n--- Ollama Server Error ---")
                print("The Ollama server ran into an internal error (500).")
                print("This often happens when your computer is low on RAM or VRAM.")
                print(
                    "💡 Please try closing other resource-intensive applications (like web browsers, games, etc.) and run the indexing again."
                )
                print("---------------------------\n")
                sys.exit(1)  # Stop the entire application
            else:
                print(f"[Ollama HTTP Error {response.status_code}: {response.text}]")
                sys.exit(1)  # Stop the entire application

            # Return a default value to prevent a crash
            return {"summary": "", "keywords": ""}

        # The response from Ollama with format='json' is a single JSON object
        json_data = response.json()

        # The actual content is in a JSON string within the 'content' field
        content_string = json_data.get("message", {}).get("content", "{}")

        # Parse the nested JSON string
        enriched_data = json.loads(content_string)
        print(enriched_data)
        return {
            "summary": enriched_data.get("summary", ""),
            "keywords": enriched_data.get("keywords", ""),
        }

    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"[Ollama enrichment error: {e}]")
        # Fallback to empty strings if the structured response fails
        return {"summary": "", "keywords": ""}
