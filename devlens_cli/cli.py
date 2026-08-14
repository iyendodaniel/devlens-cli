"""
devlens CLI - standalone terminal command for running DevLens actions.

Independent of the pywebview GUI on purpose: no SQLite, no js_api window,
no dependency on the desktop app ever having been opened. Settings live in
a plain .devlens.json file sitting in whichever project folder you run
`devlens` from.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

CONFIG_FILENAME = ".devlens.json"


# ---------------------------------------------------------------------------
# Config: read/write the small .devlens.json that remembers folder choices
# ---------------------------------------------------------------------------

def config_path():
    """Always relative to wherever you're running `devlens` FROM,
    same as how a .git folder works - it's per-project, not global."""
    return os.path.join(os.getcwd(), CONFIG_FILENAME)


def load_config():
    path = config_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_config(config):
    with open(config_path(), "w") as f:
        json.dump(config, f, indent=2)


# ---------------------------------------------------------------------------
# Folder picking: a tiny native OS dialog, not the full app window
# ---------------------------------------------------------------------------

def pick_folder(title):
    """Opens a small native folder-picker (Explorer/Finder-style), returns
    the chosen path or None if cancelled. Uses tkinter, which ships with
    Python already - nothing extra to install."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()          # don't show a blank tkinter window, just the dialog
    root.attributes("-topmost", True)  # dialog pops to the front, not hidden behind terminal
    chosen = filedialog.askdirectory(title=title)
    root.destroy()

    return chosen or None


def ensure_frontend_path(config):
    if config.get("frontend_path") and os.path.isdir(config["frontend_path"]):
        return config["frontend_path"]

    print("First time here - pick your frontend folder...")
    chosen = pick_folder("Select your frontend folder")
    if not chosen:
        print("No folder selected. Aborting.")
        sys.exit(1)

    config["frontend_path"] = chosen
    save_config(config)
    return chosen


def ensure_build_destination(config):
    if config.get("build_destination_path") and os.path.isdir(config["build_destination_path"]):
        return config["build_destination_path"]

    print("First time here - pick your backend (destination) folder...")
    chosen = pick_folder("Select your backend folder")
    if not chosen:
        print("No folder selected. Aborting.")
        sys.exit(1)

    config["build_destination_path"] = chosen
    save_config(config)
    return chosen


# ---------------------------------------------------------------------------
# The actual action: build frontend, copy dist/ into backend folder
# ---------------------------------------------------------------------------

def run_build_frontend(config):
    frontend_path = ensure_frontend_path(config)

    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    print(f"Running `npm run build` in {frontend_path} ...")

    result = subprocess.run(
        [npm_cmd, "run", "build"],
        cwd=frontend_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Build failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    print("Build succeeded.")

    dist_path = os.path.join(frontend_path, "dist")
    if not os.path.isdir(dist_path):
        print(f"Build finished but no dist/ folder found at {dist_path}")
        sys.exit(1)

    destination = ensure_build_destination(config)
    target_path = os.path.join(destination, "dist")

    shutil.copytree(dist_path, target_path, dirs_exist_ok=True)
    print(f"Copied dist/ -> {target_path}")
    print("Done.")


# Add more actions here later the same way - key is the --run value,
# value is a function that takes the config dict.
ACTIONS = {
    "frontend": run_build_frontend,
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="devlens")
    parser.add_argument(
        "--run",
        choices=list(ACTIONS.keys()),
        required=True,
        help="Which action to run.",
    )
    args = parser.parse_args()

    config = load_config()
    ACTIONS[args.run](config)


if __name__ == "__main__":
    main()
