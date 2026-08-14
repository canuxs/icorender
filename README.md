# Icorender Documentation & Wiki

Welcome to the official **Icorender** wiki. This guide covers project architecture, command-line interface usage, and feature overview.

---

## What is Icorender?

**Icorender** is a command-line interface tool designed to package and append icon files (`.ico`) directly into a binary library (`project.dll`). It provides built-in backup management and external script execution capabilities.

---

## Getting Started

Run the main CLI entry point using Python:

```bash
python main.py
```

---

## Available Commands

| Command | Syntax | Description |
| :--- | :--- | :--- |
| `add` | `add <filename.ico>` | Reads an icon from the `assets/` folder and appends its binary data to `project.dll`. |
| `backup` | `backup` | Creates a dated backup snapshot (`YYYY-MM-DD.dll`) in the `backups/` folder. |
| `backup . name` | `backup . name <name>` | Creates a custom named backup snapshot (`<name>.dll`). |
| `tools` | `tools` | Executes the external `tools.py` utility script. |
| `help` | `help` | Displays the list of supported CLI commands. |
| `exit` | `exit` | Terminates the interactive shell session. |

---

## Directory Structure

* **`assets/`**: Directory storing raw `.ico` image files.
* **`backups/`**: Contains generated `.dll` backups.
* **`project.dll`**: Target binary file where icon data is appended.
* **`icon.ico`**: Program icon used for taskbar/title bar rendering.
* **`tools.py`**: External helper script launched via the `tools` command.
