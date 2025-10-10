# app/cli.py
import typer
from src.pipeline.indexing import IndexingPipeline
from src.pipeline.querying import QueryPipeline

app = typer.Typer()


@app.command()
def index(github_url: str):
    """Indexes a GitHub repository: clones, chunks, and vectorizes it."""
    typer.echo(f"🚀 Starting indexing for: {github_url}")
    pipeline = IndexingPipeline(github_url)
    pipeline.run()
    typer.echo("✅ Indexing complete.")


@app.command()
def query(github_url: str):
    """Starts an interactive query session for an indexed repository."""
    typer.echo(f"🤔 Starting query session for: {github_url}")
    pipeline = QueryPipeline(github_url)
    try:
        pipeline.setup()
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}")
        typer.echo("Please run the 'index' command first for this repository.")
        raise typer.Exit()

    typer.echo("💡 Ask a question. Type 'exit' to quit.")
    while True:
        user_query = typer.prompt("\n> ")
        if user_query.lower() == "exit":
            break

        result = pipeline.ask(user_query)

        typer.echo("\n💬 Answer:")
        typer.echo(result["result"])
        typer.echo("\n📚 Sources:")
        for doc in result["source_documents"]:
            metadata = doc.metadata
            typer.echo(
                f"  - {metadata.get('file_path')} (Lines: {metadata.get('start_line')}-{metadata.get('end_line')})"
            )


if __name__ == "__main__":
    app()
