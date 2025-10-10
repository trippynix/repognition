# config/settings.py

# Paths
REPOS_DIR = "repos"
DATA_DIR = "data"
CHUNKS_PATH = f"{DATA_DIR}/chunks.json"
VECTORSTORE_PATH = f"{DATA_DIR}/vectorstore"

# Models
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen2.5-coder:latest"

# Ollama API
OLLAMA_API_URL = "http://localhost:11434/api/chat"
