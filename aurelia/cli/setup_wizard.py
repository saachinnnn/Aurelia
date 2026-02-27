"""Interactive setup wizard for `aurelia init`."""

import getpass

from rich.console import Console

from aurelia.cli.display import (
    print_banner,
    print_error,
    print_info,
    print_success,
    print_warning,
    create_summary_panel,
)
from aurelia.core.config import load_config, save_config, CONFIG_PATH
from aurelia.core.model import (
    AureliaConfig,
    GeminiSettings,
    OllamaSettings,
    VoyageSettings,
    bgeSettings,
)


def confirm_yes_no(console: Console, question: str, default: bool = False) -> bool:
    """Prompt for y/n confirmation. Loops until valid input."""
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        console.print(f"  {question} {hint}: ", style="dim", end="")
        answer = input().strip().lower()
        if answer == "":
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print_warning(console, "Please enter y or n.")


def prompt_choice(
    console: Console, label: str, options: list[str], default: int = 1
) -> int:
    """Display numbered options and return the 1-based selection."""
    console.print()
    console.print(f"  {label}", style="dim")
    for i, option in enumerate(options, 1):
        console.print(f"    [{i}] {option}", style="dim")

    while True:
        console.print(f"  > [{'/'.join(str(i) for i in range(1, len(options)+1))}] ({default}): ", style="dim", end="")
        answer = input().strip()
        if answer == "":
            return default
        try:
            choice = int(answer)
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print_warning(console, f"Please enter a number between 1 and {len(options)}.")


def prompt_text(
    console: Console, label: str, default: str = "", password: bool = False
) -> str:
    """Prompt for text input. Masked if password=True."""
    suffix = f" ({default})" if default else ""
    if password:
        console.print(f"  {label}: ", style="dim", end="", highlight=False)
        value = getpass.getpass(prompt="")
        return value if value else default
    else:
        console.print(f"  {label}{suffix}: ", style="dim", end="")
        value = input().strip()
        return value if value else default


def build_llm_settings(console: Console) -> dict:
    """Gather LLM provider configuration from user."""
    choice = prompt_choice(
        console,
        "Select your LLM provider:",
        [
            "Gemini API (recommended, free tier)",
            "Ollama (fully local, no API needed)",
        ],
        default=1,
    )

    if choice == 1:
        api_key = prompt_text(console, "Enter your Gemini API key", password=True)
        return {"provider": "gemini", "api_key": api_key}

    # Ollama
    base_url = prompt_text(
        console, "Ollama base URL", default="http://localhost:11434"
    )
    return {"provider": "ollama", "base_url": base_url}


def build_embedding_settings(console: Console) -> dict:
    """Gather embedding provider configuration from user."""
    choice = prompt_choice(
        console,
        "Select your embedding provider:",
        [
            "Voyage Code-3 (recommended, free tier)",
            "Local model (BGE-M3, ~500MB download)",
        ],
        default=1,
    )

    if choice == 1:
        api_key = prompt_text(console, "Enter your Voyage API key", password=True)
        return {"provider": "voyageai", "api_key": api_key}

    # Local BGE
    return {"provider": "bge"}


def show_config_summary(console: Console, config: AureliaConfig) -> None:
    """Display a summary panel of the configuration."""
    llm_provider = config.llm.provider
    llm_model = config.llm.model
    emb_provider = config.embedding.provider
    emb_model = config.embedding.model

    rows = [
        ("LLM", f"{llm_provider} ({llm_model})"),
        ("Embedding", f"{emb_provider} ({emb_model})"),
        ("Chunking", f"{config.chunking.strategy.value}, max {config.chunking.max_chunk_size} tokens"),
        ("Language", config.chunking.language),
    ]

    panel = create_summary_panel("Configuration Summary", rows)
    console.print()
    console.print(panel)
    console.print()


def run_init_wizard(console: Console) -> None:
    """Run the full init wizard."""
    print_banner(console)

    # Check for existing config
    if CONFIG_PATH.exists():
        if not confirm_yes_no(console, "Configuration already exists. Reconfigure?", default=False):
            print_info(console, "Init cancelled.")
            return

    print_info(console, "  Let's set up your environment.")

    # Gather settings
    llm_settings = build_llm_settings(console)
    embedding_settings = build_embedding_settings(console)

    # Build provider-specific settings objects
    if llm_settings["provider"] == "gemini":
        llm = GeminiSettings(api_key=llm_settings.get("api_key", ""))
    else:
        llm = OllamaSettings(base_url=llm_settings.get("base_url", "http://localhost:11434"))

    if embedding_settings["provider"] == "voyageai":
        embedding = VoyageSettings(api_key=embedding_settings.get("api_key", ""))
    else:
        embedding = bgeSettings()

    config = AureliaConfig(llm=llm, embedding=embedding)

    show_config_summary(console, config)

    if not confirm_yes_no(console, "Save this configuration?", default=True):
        print_info(console, "Configuration not saved.")
        return

    save_config(config)
    print_success(console, f"  Configuration saved to {CONFIG_PATH}")
    console.print()
    print_info(console, "  Run `aurelia index <path>` to index your first repository.")
