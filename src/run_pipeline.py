# run_pipeline.py
import os
from core.ingest import RepoIngestor
from core.vectorize import Vectorizer


class RepoPipeline:
    """Full pipeline: clone GitHub repo, chunk, and vectorize."""

    def __init__(self, github_url):
        self.github_url = github_url
        self.vectorizer = Vectorizer()

    def run(self):
        # -----------------------------
        # 1️⃣ Ingest repo
        # -----------------------------
        print("🚀 Starting repo ingestion...")
        ingestor = RepoIngestor(self.github_url)
        # chunks = ingestor.run()  # clones, parses, and saves chunks
        print(f"✅ Repo ingested and chunks saved at {ingestor.save_path}")

        # -----------------------------
        # 2️⃣ Vectorize chunks
        # -----------------------------
        print("⚡ Starting vectorization...")
        if os.path.exists(
            os.path.join(
                self.vectorizer.db_path, f"{self.github_url.split('/')[-1]}_vectorstore"
            )
        ):
            print("🔄 FAISS vectorstore already exists, loading...")
            vectorstore = self.vectorizer.load(self.github_url)
        else:
            print("⚡ Creating new FAISS vectorstore...")
            vectorstore = self.vectorizer.build(self.github_url)  # pass chunks directly

        print("🎯 Pipeline completed successfully!")
        return vectorstore


if __name__ == "__main__":
    # github_url = input("Enter GitHub repo URL: ").strip()
    github_url = "https://github.com/trippynix/HR_assistant_chatbot"
    pipeline = RepoPipeline(github_url)
    vectorstore = pipeline.run()
    print(vectorstore)
