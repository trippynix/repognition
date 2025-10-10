# src/pipeline/querying.py
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from src.components.vectorstore import VectorstoreManager
from config.settings import LLM_MODEL


class QueryPipeline:
    def __init__(self, github_url):
        self.github_url = github_url
        self.repo_name = github_url.split("/")[-1]
        self.vectorstore_manager = VectorstoreManager()
        self.llm = Ollama(model=LLM_MODEL)
        self.qa_chain = None

    def setup(self):
        """Loads the vectorstore and sets up the QA chain."""
        vectorstore = self.vectorstore_manager.load(self.repo_name)
        if not vectorstore:
            raise FileNotFoundError(f"Vectorstore for '{self.repo_name}' not found.")

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
        )
        print("QA chain is ready.")

    def ask(self, query_text):
        """Asks a question and returns the response."""
        if not self.qa_chain:
            raise ValueError("QA chain is not set up. Call setup() first.")

        response = self.qa_chain.invoke(query_text)
        return response
