# devlens-cli

A standalone terminal command for running DevLens actions — independent of the
DevLens desktop app (pywebview GUI). Built as a fallback for when the GUI
window won't pop up, and for anyone who just prefers the terminal.

## What it does

Right now it supports one action: building your frontend and copying the
`dist/` output into your backend folder.

```
devlens --run frontend
```

- **First run in a project:** a small native folder-picker window pops up
  asking for your frontend folder, then another for your backend
  (destination) folder. It builds, copies, and saves both paths into a
  `.devlens.json` file in that project's root.
- **Every run after that:** no popups — it reads `.devlens.json` and just
  builds + copies straight through.

## Install

Clone or download this repo, then from inside the `devlens-cli/` folder
(make sure you're **not** inside an unrelated venv unless you specifically
want it scoped to that venv):

```
pip install -e .
```

This registers `devlens` as a real terminal command via
`[project.scripts]` in `pyproject.toml`. The `-e` (editable) flag means it
runs directly from this source folder — no reinstall needed after editing
`cli.py`.

Open a new terminal window/tab after installing so it picks up the command.

## Usage

`cd` into any project folder and run:

```
devlens --run frontend
```

## Config file (`.devlens.json`)

Created automatically on first run, per project. It looks like:

```json
{
  "frontend_path": "C:\\path\\to\\frontend",
  "build_destination_path": "C:\\path\\to\\backend"
}
```

Delete this file (or edit the paths inside it) if you ever need to point at
different folders — the CLI will just ask again via the folder picker.

## Requirements

- Python 3.8+
- `npm` available on your PATH
- tkinter (ships with standard Python installs — no extra install needed)

## Notes

- No SQLite, no dependency on the DevLens desktop app ever having been
  opened — this is a clean, separate entry point into the same
  build-and-copy logic.
- Add more actions later by writing a new function and adding it to the
  `ACTIONS` dict in `cli.py`.