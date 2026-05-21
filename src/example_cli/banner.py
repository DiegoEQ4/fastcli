import sys
from pathlib import Path

# Try to load package version dynamically
VERSION = "0.1.0"
DESCRIPTION = "CLI para generar proyectos FastAPI con plantillas y utilidades"

try:
    if sys.version_info >= (3, 8):
        import importlib.metadata
        try:
            VERSION = importlib.metadata.version("fastcli")
            DESCRIPTION = importlib.metadata.metadata("fastcli")["Summary"]
        except importlib.metadata.PackageNotFoundError:
            # Fallback to reading pyproject.toml if running in dev environment
            pyproject_path = Path(__file__).parents[2] / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line_stripped = line.strip()
                        if line_stripped.startswith("version ="):
                            VERSION = line_stripped.split("=")[1].strip().strip('"').strip("'")
                        elif line_stripped.startswith("description ="):
                            DESCRIPTION = line_stripped.split("=")[1].strip().strip('"').strip("'")
except Exception:
    pass

# Color Palettes (RGB)
PALETTES = {
    "pastel_blue": (92, 135, 201),      # Soft dark pastel blue
    "pastel_cyan": (100, 180, 200),      # Soft cyan
    "pastel_green": (110, 190, 140),     # Soft pastel green
    "pastel_purple": (150, 130, 200),    # Soft purple/lavender
}

# ASCII Art Templates
BANNERS = {
    "FASTCLI": r"""
  ______               _      _____  _      _____ 
 |  ____|             | |    / ____|| |    |_   _|
 | |__  __ _  ___  ___| |_  | |     | |      | |  
 |  __|/ _` |/ __|/ __| __| | |     | |      | |  
 | |  | (_| |\__ \ (__| |_  | |____ | |____ _| |_ 
 |_|   \__,_||___/\___|\__|  \_____||______|_____|
""",
    "FASTAPI": r"""
  ______      _____ _______       _____ _____ 
 |  ____/\   / ____|__   __|/\   |  __ \_   _|
 | |__ /  \ | (___    | |  /  \  | |__) || |  
 |  __/ /\ \ \___ \   | | / /\ \ |  ___/ | |  
 | | / ____ \____) |  | |/ ____ \| |    _| |_ 
 |_|/_/    \_\_____/  |_/_/    \_\_|   |_____|
"""
}

def get_color_escape(rgb_tuple: tuple) -> str:
    """Returns the ANSI escape sequence for a 24-bit RGB foreground color."""
    r, g, b = rgb_tuple
    return f"\033[38;2;{r};{g};{b}m"

def print_banner(name: str = "FASTCLI", theme: str = "pastel_blue"):
    """
    Prints a beautiful, dynamic CLI banner.
    
    Args:
        name: The name of the banner key in BANNERS.
        theme: Key in PALETTES for color styling.
    """
    reset = "\033[0m"
    bold = "\033[1m"
    dim = "\033[2m"
    
    # Get theme color
    rgb = PALETTES.get(theme, PALETTES["pastel_blue"])
    primary_color = get_color_escape(rgb)
    
    # Get secondary color (slightly dimmer/different shade or white)
    secondary_color = "\033[38;2;160;185;220m" if theme == "pastel_blue" else "\033[37m"
    
    # Retrieve ASCII art
    ascii_art = BANNERS.get(name.upper(), BANNERS["FASTCLI"])
    
    # Print the colored banner
    print(f"{primary_color}{ascii_art}{reset}")
    
    # Print dynamic system information underneath
    print(f"  {bold}{primary_color}»{reset} {bold}Version:{reset} {secondary_color}{VERSION}{reset} | {dim}{DESCRIPTION}{reset}")
    print(f"  {bold}{primary_color}»{reset} {dim}Ready to build clean, fast APIs.{reset}\n")
