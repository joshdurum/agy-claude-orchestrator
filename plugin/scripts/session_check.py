#!/usr/bin/env python3
"""
Global SessionStart Inspector for Antigravity and Claude Code on macOS (M4 Max, 36GB RAM).
Reads workspace path from hook stdin JSON (cwd / workspacePaths) before falling back to os.getcwd().
Checks Mentor Mode toggle state, active git worktrees, and whether the current
project has customized ## Verification Gates in its root AGENTS.md.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_MARKERS = [
    ".git",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Package.swift",
    "Makefile",
    "justfile",
    "Dockerfile",
]


def resolve_workspace_cwd() -> Path:
    """Resolve the active workspace directory from hook stdin JSON or os.getcwd()."""
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read().strip()
            if raw:
                data = json.loads(raw)
                if isinstance(data, dict):
                    ws_paths = data.get("workspacePaths")
                    if isinstance(ws_paths, list) and ws_paths and isinstance(ws_paths[0], str) and ws_paths[0].strip():
                        p = Path(ws_paths[0]).expanduser()
                        if p.exists():
                            return p
                    cwd_val = data.get("cwd")
                    if isinstance(cwd_val, str) and cwd_val.strip():
                        p = Path(cwd_val).expanduser()
                        # Ignore the plugin or config directory if Antigravity ran the hook from hooks.json dir
                        if p.exists() and ".gemini/config" not in str(p):
                            return p
        except Exception:
            pass
    return Path(os.getcwd())



def load_profile() -> dict:
    cfg = Path.home() / ".gemini" / "config" / "orchestrator_profile.json"
    defaults = {
        "machine_label": "Mac Studio M4 Max",
        "ram_gb": 36,
        "max_worktrees": 3,
        "account_tier": "Personal Pro",
    }
    if not cfg.exists():
        return defaults
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        return {**defaults, **data}
    except Exception:
        return defaults


def get_mentor_mode() -> bool:
    cfg = Path.home() / ".gemini" / "config" / "mentor_mode.json"
    if not cfg.exists():
        return True
    try:
        return bool(json.loads(cfg.read_text(encoding="utf-8")).get("enabled", True))
    except Exception:
        return True


def get_worktree_count(cwd: Path) -> int:
    try:
        res = subprocess.run(
            ["git", "worktree", "list"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0:
            lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
            return max(1, len(lines))
    except Exception:
        pass
    return 1


def is_code_project(cwd: Path) -> bool:
    if any((cwd / marker).exists() for marker in PROJECT_MARKERS):
        return True
    if any(cwd.glob("*.xcodeproj")) or any(cwd.glob("*.xcworkspace")):
        return True
    return False


def extract_gates(agents_file: Path) -> str | None:
    if not agents_file.exists():
        return None
    try:
        text = agents_file.read_text(encoding="utf-8")
        match = re.search(
            r"(## Verification Gates[\s\S]*?)(?=\n## |\Z)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None


def build_message(cwd: Path) -> str:
    mentor_on = get_mentor_mode()
    mentor_tag = (
        "Mentor Mode: ON (Beginner Teacher — explain actions before/after, define jargon, teach concepts; toggle via /mentor-mode)"
        if mentor_on
        else "Mentor Mode: OFF (Standard Developer Mode — concise technical summaries; toggle via /mentor-mode)"
    )
    prof = load_profile()
    max_wt = int(prof.get("max_worktrees", 3))
    ram_gb = int(prof.get("ram_gb", 36))
    badge = f"[{prof.get('machine_label', 'Local Machine')} | {ram_gb}GB | {prof.get('account_tier', 'Pro')}]"
    wt_count = get_worktree_count(cwd)
    wt_status = f"Active git worktrees: {wt_count}/{max_wt}"
    if wt_count >= max_wt:
        wt_status += f" (AT {ram_gb}GB RAM CAP — run /cleanup-worktrees before creating new ones)"

    if not is_code_project(cwd):
        return f"{badge} Directory `{cwd.name}` (no repo manifest detected). {mentor_tag}. {wt_status}."

    agents_file = cwd / "AGENTS.md"
    gates = extract_gates(agents_file)
    if gates:
        compact_gates = " | ".join(
            ln.strip() for ln in gates.splitlines()[1:] if ln.strip()
        )
        return (
            f"{badge} Project `{cwd.name}` onboarded. "
            f"{mentor_tag}. {wt_status}. Active Gates: {compact_gates}"
        )

    return (
        f"{badge} ACTION REQUIRED: Project `{cwd.name}` "
        f"does not have customized `## Verification Gates` in `./AGENTS.md` yet. "
        f"{mentor_tag}. {wt_status}. Before making code changes, inspect the repo manifests and run "
        f"`/init-project-gates` to tailor build, lint, test, dev-server, and worktree bootstrap gates."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SessionStart inspector for Antigravity & Claude Code.")
    parser.add_argument(
        "--client",
        choices=["antigravity", "claude"],
        default="antigravity",
        help="Target CLI/IDE hook schema format",
    )
    args = parser.parse_args()
    cwd = resolve_workspace_cwd()
    msg = build_message(cwd)

    if args.client == "claude":
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": msg,
            }
        }
    else:
        payload = {
            "injectSteps": [
                {
                    "systemMessage": {
                        "systemMessage": msg,
                    }
                }
            ]
        }

    print(json.dumps(payload))


if __name__ == "__main__":
    main()
