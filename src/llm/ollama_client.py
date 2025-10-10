# src/llm/ollama_client.py
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


def generate_summary(code_chunk: str) -> str:
    """
    Summarize a code chunk concisely.
    """
    if not code_chunk.strip():
        return ""
    prompt = (
        "Summarize the following Python code chunk in one concise sentence. "
        "If it is markdown, reply 'markdown'. Explain only what it does:\n\n"
        + code_chunk
    )
    return stream_ollama_response(prompt)


def extract_keywords(code_chunk: str) -> str:
    """
    Extract identifiers, functions, class names, and keywords.
    """
    if not code_chunk.strip():
        return ""
    prompt = (
        "List the main identifiers, function names, class names, and important keywords "
        "from this code chunk as a comma-separated list:\n\n" + code_chunk
    )
    return stream_ollama_response(prompt)
