#!/usr/bin/env python3
"""Cleanly removes orchestrator symlinks and plugin while preserving user backups."""
import shutil
from pathlib import Path

HOME = Path.home()
PLUGIN_DIR = HOME / ".gemini" / "config" / "plugins" / "mac-studio-orchestrator"
SKILLS = [
    "build-prompt",
    "claude-handoff",
    "cleanup-worktrees",
    "gemini-handoff",
    "init-project-gates",
    "mentor-mode",
    "route-task",
    "undo-last",
]


def main() -> None:
    print("=== Uninstalling Antigravity + Claude Code Orchestrator ===")
    for link in [
        HOME / ".gemini" / "GEMINI.md",
        HOME / ".gemini" / "scripts",
        HOME / ".local" / "bin" / "route",
        HOME / ".local" / "bin" / "prompt-forge",
        *[HOME / ".claude" / "skills" / s for s in SKILLS],
    ]:
        if link.is_symlink():
            link.unlink()
            print(f"  [Removed Symlink] {link}")

    if PLUGIN_DIR.exists():
        shutil.rmtree(PLUGIN_DIR)
        print(f"  [Removed Plugin ] {PLUGIN_DIR}")

    print("Done! Any previous config backups remain safe in ~/.gemini/backups/.")


if __name__ == "__main__":
    main()
