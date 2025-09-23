import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:latest"


def stream_ollama_response(prompt: str) -> str:
    """
    Send a streaming request to Ollama and capture the full response text.
    """
    payload = {
        "model": MODEL_NAME,
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
                        print(chunk, end="", flush=True)  # live printing
                        collected_text.append(chunk)
                except json.JSONDecodeError:
                    print("\n[Non-JSON line received:]", line)
        print()  # newline after stream ends
        return "".join(collected_text).strip()
    else:
        return f"[ollama error {response.status_code}: {response.text}]"


def generate_summary(code_chunk: str) -> str:
    """
    Summarize a code chunk concisely using CodeLlama 7B via Ollama streaming.
    """
    if not code_chunk.strip():
        return ""

    prompt = (
        "Summarize the following Python code chunk in one concise sentence. If there's no code but a markdown content from a readme ignore and reply 'markdown'"
        "Only explain what it does, no extra words:\n\n" + code_chunk
    )
    return stream_ollama_response(prompt)


def extract_keywords(code_chunk: str) -> str:
    """
    Extract identifiers, functions, class names, and keywords from a code chunk.
    """
    if not code_chunk.strip():
        return ""

    prompt = (
        "List the main identifiers, function names, class names, and important keywords "
        "from this Python code chunk as a comma-separated list:\n\n" + code_chunk
    )
    return stream_ollama_response(prompt)
