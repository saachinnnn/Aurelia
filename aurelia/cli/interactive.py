"""Interactive prompt loop using prompt_toolkit."""

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console

from aurelia.cli.display import (
    print_banner,
    print_tips,
    print_error,
    print_info,
    print_warning,
)
from aurelia.core.config import CONFIG_DIR

HISTORY_FILE = CONFIG_DIR / ".history"

PROMPT_STYLE = Style.from_dict({"prompt": "#4285f4"})
PROMPT_MESSAGE = [("class:prompt", "> ")]

SLASH_COMMANDS = {
    "/help": "Show available commands.",
    "/quit": "Exit interactive mode.",
    "/clear": "Clear the terminal screen.",
}


def handle_slash_command(command: str, console: Console) -> bool:
    """Process a slash command. Returns False if the loop should exit."""
    cmd = command.strip().lower()

    if cmd == "/quit":
        return False

    if cmd == "/clear":
        console.clear()
        return True

    if cmd == "/help":
        console.print()
        console.print("  Available commands:", style="dim")
        for name, description in SLASH_COMMANDS.items():
            console.print(f"    {name:<10} {description}", style="dim")
        console.print()
        return True

    print_warning(console, f"Unknown command: {command}. Type /help for available commands.")
    return True


def start_interactive_loop(console: Console) -> None:
    """Run the interactive prompt loop."""
    print_tips(console)

    session = PromptSession(
        history=FileHistory(str(HISTORY_FILE)),
    )

    while True:
        try:
            user_input = session.prompt(PROMPT_MESSAGE, style=PROMPT_STYLE)
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print()
            break

        text = user_input.strip()
        if not text:
            continue

        if text.startswith("/"):
            should_continue = handle_slash_command(text, console)
            if not should_continue:
                break
            continue

        print_info(
            console,
            "Not yet implemented. Run `aurelia index <path>` first, then ask questions.",
        )
