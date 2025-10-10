import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.indexing import IndexingPipeline
from src.pipeline.querying import QueryPipeline

# --- Page Configuration ---
st.set_page_config(
    page_title="AI DevAssistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS for styling ---
st.markdown(
    """
<style>
    .stButton>button {
        width: 100%;
    }
    .stExpander {
        border: 1px solid #e6e6e6;
        border-radius: 0.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Session State Initialization ---
if "query_pipeline" not in st.session_state:
    st.session_state.query_pipeline = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_repo" not in st.session_state:
    st.session_state.indexed_repo = None


# --- Sidebar ---
with st.sidebar:
    st.header("AI DevAssistant 🤖")
    st.markdown(
        "Your AI-powered copilot for understanding and navigating complex codebases."
    )

    repo_url = st.text_input(
        "Enter a GitHub Repository URL", placeholder="https://github.com/user/repo"
    )

    if st.button("Index Repository"):
        if repo_url:
            with st.spinner(
                f"Starting indexing for `{repo_url}`... This may take a while."
            ):
                try:
                    # Clear previous state
                    st.session_state.query_pipeline = None
                    st.session_state.messages = []
                    st.session_state.indexed_repo = None

                    # --- Run Indexing Pipeline ---
                    st.info("Step 1/3: Cloning repository...")
                    indexing_pipeline = IndexingPipeline(repo_url)

                    st.info("Step 2/3: Chunking, enriching, and vectorizing files...")
                    indexing_pipeline.run()

                    st.info("Step 3/3: Setting up query engine...")
                    query_pipeline = QueryPipeline(repo_url)
                    query_pipeline.setup()

                    # --- Store in session state on success ---
                    st.session_state.query_pipeline = query_pipeline
                    st.session_state.indexed_repo = repo_url
                    st.success(
                        f"Successfully indexed `{repo_url}`! You can now ask questions."
                    )

                except FileNotFoundError:
                    st.error(
                        "Indexing failed. Could not find the vector store. Please ensure the indexing process completes successfully."
                    )
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a GitHub repository URL.")

    st.markdown("---")
    st.markdown(
        "Created by [Amey Tonannavar](https://github.com/trippynix) | "
        "[View Source](https://github.com/your-username/AI-DevAssistant)"
    )


# --- Main Chat Interface ---
st.title("Chat with your Codebase")
st.markdown(
    "Ask questions about the indexed repository. The assistant will find relevant code snippets and explain them."
)

if st.session_state.indexed_repo:
    st.info(f"Currently chatting with: `{st.session_state.indexed_repo}`")
else:
    st.info("Index a repository from the sidebar to begin.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Sources"):
                for doc in message["sources"]:
                    metadata = doc.metadata
                    file_path = metadata.get("file_path", "N/A").replace("\\", "/")
                    start_line = metadata.get("start_line", "N/A")
                    end_line = metadata.get("end_line", "N/A")
                    st.markdown(
                        f"- **File:** `{file_path}` (Lines: {start_line}-{end_line})"
                    )
                    st.code(doc.page_content, language="plaintext")


# Accept user input
if prompt := st.chat_input("Ask a question about the code..."):
    if st.session_state.query_pipeline:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.query_pipeline.ask(prompt)
                    answer = response.get("result", "Sorry, I couldn't find an answer.")
                    sources = response.get("source_documents", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander("View Sources"):
                            for doc in sources:
                                metadata = doc.metadata
                                # Normalize file path for consistent display
                                file_path = metadata.get("file_path", "N/A").replace(
                                    "\\", "/"
                                )
                                start_line = metadata.get("start_line", "N/A")
                                end_line = metadata.get("end_line", "N/A")
                                st.markdown(
                                    f"- **File:** `{file_path}` (Lines: {start_line}-{end_line})"
                                )
                                # Display the raw content of the source document
                                st.code(doc.page_content, language="plaintext")

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )

                except Exception as e:
                    st.error(f"An error occurred while querying: {e}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"Error: {e}"}
                    )

    else:
        st.warning("Please index a repository first before asking questions.")
