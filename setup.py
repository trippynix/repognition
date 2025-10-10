# setup.py
from setuptools import setup, find_packages

setup(
    name="ai_dev_assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "pathspec==0.12.1",
        "gitpython==3.1.45",
        "langchain==0.3.27",
        "langchain-text-splitters==0.3.11",
        "ollama==0.5.4",
        "langchain-community==0.3.29",
        "faiss-cpu",
        "langchain-ollama",
        "requests",
        "typer",
        "streamlit",
    ],
    entry_points={
        "console_scripts": [
            "ai-dev-assistant = app.cli:app",
        ],
    },
)
