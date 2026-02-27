"""Aurelia CLI — Typer application with all command registrations."""

from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()

app = typer.Typer(
    name="aurelia",
    help="AST-aware RAG engine for intelligent codebase conversations.",
    add_completion=False,
    no_args_is_help=False,
)

config_app = typer.Typer(
    name="config",
    help="View and manage Aurelia configuration.",
)
app.add_typer(config_app, name="config")


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """Interactive mode — ask questions about your codebase."""
    if ctx.invoked_subcommand is not None:
        return
    from aurelia.cli.display import print_banner
    from aurelia.cli.interactive import start_interactive_loop

    print_banner(console)
    start_interactive_loop(console)


@app.command()
def init() -> None:
    """Initialize Aurelia configuration through an interactive wizard."""
    from aurelia.cli.setup_wizard import run_init_wizard

    run_init_wizard(console)


@app.command()
def index(
    path: str = typer.Argument(..., help="Path to the repository to index."),
) -> None:
    """Index a codebase for retrieval."""
    from aurelia.cli.display import print_info, print_warning

    print_info(console, f"Indexing repository: {path}")
    print_warning(console, "Not yet implemented.")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question about your codebase."),
    show_chunks: bool = typer.Option(
        False, "--show-chunks", "-s", help="Display retrieved source chunks."
    ),
    filter_lang: Optional[str] = typer.Option(
        None, "--filter-lang", "-l", help="Filter by programming language."
    ),
    filter_author: Optional[str] = typer.Option(
        None, "--filter-author", "-a", help="Filter by git author."
    ),
    top_k: int = typer.Option(
        5, "--top-k", "-k", help="Number of chunks to retrieve."
    ),
    no_stream: bool = typer.Option(
        False, "--no-stream", help="Disable streaming output."
    ),
) -> None:
    """Ask a question about your indexed codebase."""
    from aurelia.cli.display import print_info, print_warning

    print_info(console, f"Question: {question}")
    print_warning(console, "Not yet implemented.")


@app.command()
def stats() -> None:
    """Show statistics about the indexed codebase."""
    table = Table(title="Index Statistics", border_style="dim", show_header=False)
    table.add_column("Key", style="dim")
    table.add_column("Value")
    table.add_row("Status", "Not indexed")
    table.add_row("Total files", "\u2014")
    table.add_row("Total chunks", "\u2014")
    table.add_row("Languages", "\u2014")
    table.add_row("Last indexed", "\u2014")
    table.add_row("Index location", "\u2014")
    console.print()
    console.print(table)
    console.print()


@app.command()
def reindex(
    full: bool = typer.Option(
        False, "--full", "-f", help="Full reindex instead of incremental."
    ),
) -> None:
    """Reindex the current codebase."""
    from aurelia.cli.display import print_info, print_warning

    mode = "Full reindex" if full else "Incremental reindex (changed files only)"
    print_info(console, mode)
    print_warning(console, "Not yet implemented.")


@app.command(name="eval")
def eval_cmd(
    eval_file: str = typer.Option(
        "./aurelia_eval.yaml", "--eval-file", "-e", help="Path to evaluation YAML."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose output."
    ),
) -> None:
    """Run evaluation suite against the indexed codebase."""
    from aurelia.cli.display import print_info, print_warning

    print_info(console, "Running evaluation suite...")
    print_info(console, f"Eval file: {eval_file}")
    print_warning(console, "Not yet implemented.")


# ── Config subcommands ──────────────────────────────────────────────


@config_app.command("show")
def config_show() -> None:
    """Display the current Aurelia configuration."""
    from aurelia.core.config import load_config, CONFIG_PATH

    config = load_config()
    yaml_str = yaml.safe_dump(
        config.model_dump(mode="json"), default_flow_style=False, sort_keys=False
    )
    syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=False)
    console.print()
    console.print(
        Panel(syntax, title=str(CONFIG_PATH), border_style="dim", padding=(1, 2))
    )
    console.print()


@config_app.command("reset")
def config_reset() -> None:
    """Reset configuration to defaults."""
    from aurelia.core.config import save_config, CONFIG_PATH
    from aurelia.core.model import AureliaConfig
    from aurelia.cli.display import print_success, print_info

    if CONFIG_PATH.exists():
        confirm = typer.confirm(
            "This will reset all settings to defaults. Continue?"
        )
        if not confirm:
            print_info(console, "Reset cancelled.")
            raise typer.Abort()

    save_config(AureliaConfig())
    print_success(console, f"Configuration reset to defaults at {CONFIG_PATH}")
