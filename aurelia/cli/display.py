"""Banner rendering, gradient coloring, and Rich formatting utilities."""

import shutil

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

VERSION = "0.1.0"

GRADIENT_COLORS = ["#4285f4", "#9b72cb", "#d96570"]

# Hardcoded ANSI Shadow banner for "AURELIA" — fallback if pyfiglet is unavailable.
BANNER_LARGE = r"""
 █████╗ ██╗   ██╗██████╗ ███████╗██╗     ██╗ █████╗
██╔══██╗██║   ██║██╔══██╗██╔════╝██║     ██║██╔══██╗
███████║██║   ██║██████╔╝█████╗  ██║     ██║███████║
██╔══██║██║   ██║██╔══██╗██╔══╝  ██║     ██║██╔══██║
██║  ██║╚██████╔╝██║  ██║███████╗███████╗██║██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═╝
""".strip("\n")

BANNER_SMALL = r"""
  _  _   _ ___ ___ _    ___   _
 /_\| | | | _ \ __| |  |_ _| /_\
/ _ \ |_| |   / _|| |__ | | / _ \
/_/ \_\___/|_|_\___|____|___/_/ \_\
""".strip("\n")


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string like '#4285f4' to an (R, G, B) tuple."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def interpolate_color(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    """Linear RGB interpolation between two colors. t in [0.0, 1.0]."""
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def get_gradient_color(
    col: int, total_cols: int, colors: list[tuple[int, int, int]]
) -> tuple[int, int, int]:
    """Return the interpolated RGB color for a given column position
    across a multi-stop gradient."""
    if total_cols <= 1 or len(colors) < 2:
        return colors[0]
    t = col / (total_cols - 1)
    num_segments = len(colors) - 1
    segment = min(int(t * num_segments), num_segments - 1)
    local_t = (t * num_segments) - segment
    return interpolate_color(colors[segment], colors[segment + 1], local_t)


def generate_banner_text() -> str:
    """Generate the AURELIA banner using pyfiglet, with hardcoded fallback."""
    try:
        import pyfiglet

        text = pyfiglet.figlet_format("AURELIA", font="ansi_shadow")
        # Strip trailing blank lines but keep structure
        return text.rstrip("\n")
    except Exception:
        return BANNER_LARGE


def apply_gradient(text: str, colors: list[str] | None = None) -> Text:
    """Apply a horizontal per-character gradient to multi-line ASCII art.

    Returns a Rich Text object with per-character RGB styling.
    """
    if colors is None:
        colors = GRADIENT_COLORS

    rgb_colors = [hex_to_rgb(c) for c in colors]
    lines = text.split("\n")
    max_width = max(len(line) for line in lines) if lines else 1

    result = Text()
    for i, line in enumerate(lines):
        for col, char in enumerate(line):
            if char.isspace():
                result.append(char)
            else:
                r, g, b = get_gradient_color(col, max_width, rgb_colors)
                result.append(char, style=f"rgb({r},{g},{b})")
        if i < len(lines) - 1:
            result.append("\n")

    return result


def get_banner_for_width(terminal_width: int) -> str:
    """Select the appropriate banner size for the terminal width."""
    large = generate_banner_text()
    large_width = max(len(line) for line in large.split("\n"))

    if terminal_width >= large_width + 2:
        return large

    small_width = max(len(line) for line in BANNER_SMALL.split("\n"))
    if terminal_width >= small_width + 2:
        return BANNER_SMALL

    return "AURELIA"


def print_banner(console: Console) -> None:
    """Print the gradient banner followed by version and tagline."""
    terminal_width = shutil.get_terminal_size().columns
    banner_text = get_banner_for_width(terminal_width)
    gradient_banner = apply_gradient(banner_text)

    console.print()
    console.print(gradient_banner)
    console.print()
    console.print(f"  Aurelia v{VERSION} — Talk to your codebase", style="dim")
    console.print()


def print_tips(console: Console) -> None:
    """Print the startup tips in dim text."""
    console.print("  Tips for getting started:", style="dim")
    console.print("    1. Ask questions about your indexed codebase.", style="dim")
    console.print("    2. Be specific for the best results.", style="dim")
    console.print("    3. /help for more information.", style="dim")
    console.print()


def print_error(console: Console, message: str) -> None:
    """Print an error message in red."""
    console.print(f"Error: {message}", style="red")


def print_success(console: Console, message: str) -> None:
    """Print a success message in green."""
    console.print(message, style="green")


def print_warning(console: Console, message: str) -> None:
    """Print a warning message in yellow."""
    console.print(message, style="yellow")


def print_info(console: Console, message: str) -> None:
    """Print an informational message in dim text."""
    console.print(message, style="dim")


def create_summary_panel(title: str, rows: list[tuple[str, str]]) -> Panel:
    """Create a dim-bordered Rich Panel containing a key-value table."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")
    for key, value in rows:
        table.add_row(key, value)
    return Panel(table, title=title, border_style="dim", padding=(1, 2))
