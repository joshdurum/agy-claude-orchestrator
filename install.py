#!/usr/bin/env python3
"""
Portable, Customizable Installer for Antigravity + Claude Code Orchestrator & PromptForge.
Works on any macOS or Linux setup, automatically backing up existing configs and merging
into ~/.claude/settings.json without clobbering existing user preferences.
"""
import argparse
import datetime
import json
import os
import platform
import shutil
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
HOME = Path.home()
GEMINI_DIR = HOME / ".gemini"
CONFIG_DIR = GEMINI_DIR / "config"
PLUGINS_DIR = CONFIG_DIR / "plugins"
TARGET_PLUGIN = PLUGINS_DIR / "mac-studio-orchestrator"
CLAUDE_DIR = HOME / ".claude"
LOCAL_BIN = HOME / ".local" / "bin"
TS = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP_DIR = GEMINI_DIR / "backups" / TS


def recommend_worktrees_for_ram(ram_gb: int) -> int:
    if ram_gb <= 16:
        return 1
    if ram_gb <= 24:
        return 2
    if ram_gb <= 48:
        return 3
    if ram_gb <= 64:
        return 5
    return 8


def backup_path(path: Path) -> None:
    if path.exists() and not path.is_symlink():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        dest = BACKUP_DIR / path.name
        if path.is_dir():
            shutil.copytree(path, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(path, dest)
        print(f"  [Backup] Saved {path} -> {dest}")


def ensure_symlink(target: Path, link_path: Path) -> None:
    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink() and link_path.resolve() == target.resolve():
            return
        backup_path(link_path)
        if link_path.is_dir() and not link_path.is_symlink():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()
    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.symlink_to(target)
    print(f"  [Link  ] {link_path} -> {target}")


def merge_claude_settings() -> None:
    settings_path = CLAUDE_DIR / "settings.json"
    backup_path(settings_path)
    existing = {}
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    hooks = existing.get("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}

    session_start_cmd = "python3 ~/.gemini/scripts/session_check.py --client claude"
    hooks["SessionStart"] = [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": session_start_cmd,
                }
            ]
        }
    ]
    existing["hooks"] = hooks

    perms = existing.get("permissions", {})
    if not isinstance(perms, dict):
        perms = {}
    deny_list = perms.get("deny", [])
    if not isinstance(deny_list, list):
        deny_list = []
    for rule in [
        "Bash(rm -rf /)",
        "Bash(rm -rf ~)",
        "Bash(rm -rf *)",
        "Bash(git push --force*)",
        "Bash(git push -f*)",
    ]:
        if rule not in deny_list:
            deny_list.append(rule)
    perms["deny"] = deny_list
    existing["permissions"] = perms

    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"  [Merge ] Updated {settings_path} (preserved existing user settings)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install and customize the Antigravity + Claude Code Orchestrator & PromptForge plugin."
    )
    parser.add_argument("--machine", default="Mac Studio M4 Max", help="Machine label shown in session banners (e.g. 'MacBook Pro M3', 'Linux Workstation')")
    parser.add_argument("--ram", type=int, default=36, help="System RAM in GB (auto-calculates safe Git worktree cap if --max-worktrees is omitted)")
    parser.add_argument("--max-worktrees", type=int, default=None, help="Maximum concurrent Git worktrees allowed")
    parser.add_argument("--account-tier", default="Personal Pro (Claude + Gemini)", help="Account tier label")
    parser.add_argument("--default-claude-model", default="sonnet", choices=["sonnet", "opus", "haiku"], help="Default Claude model for standard coding tasks")
    parser.add_argument("--default-architect-model", default="opus", choices=["opus", "sonnet"], help="Default Claude model for deep architecture & debugging")
    parser.add_argument("--edit-strategy", default="in_branch_with_stash", choices=["in_branch_with_stash", "always_worktree"], help="Whether standard coding tasks edit in-branch (with git stash backup) or always spawn a worktree")
    parser.add_argument("--mentor", default="on", choices=["on", "off"], help="Initial Beginner Mentor Mode state (default: on)")
    args = parser.parse_args()

    max_wt = args.max_worktrees if args.max_worktrees is not None else recommend_worktrees_for_ram(args.ram)

    print("=== Installing Antigravity + Claude Code Orchestrator & PromptForge ===")
    for d in [CONFIG_DIR, PLUGINS_DIR, CLAUDE_DIR, LOCAL_BIN]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Copy plugin bundle
    if TARGET_PLUGIN.exists():
        backup_path(TARGET_PLUGIN)
        shutil.rmtree(TARGET_PLUGIN)
    shutil.copytree(REPO_ROOT / "plugin", TARGET_PLUGIN)
    print(f"  [Plugin] Installed {TARGET_PLUGIN}")

    # 2. Make scripts executable
    for script in (TARGET_PLUGIN / "scripts").glob("*.py"):
        script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 3. Remove standalone ~/.gemini/config/hooks.json if present so plugin hooks don't fire twice
    loose_hooks = CONFIG_DIR / "hooks.json"
    if loose_hooks.exists():
        backup_path(loose_hooks)
        loose_hooks.unlink()

    # 4. Symlink skills into ~/.claude/skills/<skill> without deleting user's other Claude skills
    claude_skills = CLAUDE_DIR / "skills"
    if claude_skills.is_symlink():
        claude_skills.unlink()
    claude_skills.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted((TARGET_PLUGIN / "skills").iterdir()):
        if skill_dir.is_dir():
            ensure_symlink(skill_dir, claude_skills / skill_dir.name)

    ensure_symlink(TARGET_PLUGIN / "scripts", GEMINI_DIR / "scripts")
    ensure_symlink(TARGET_PLUGIN / "rules" / "AGENTS.md", GEMINI_DIR / "GEMINI.md")
    ensure_symlink(TARGET_PLUGIN / "scripts" / "route.py", LOCAL_BIN / "route")
    ensure_symlink(TARGET_PLUGIN / "scripts" / "prompt_builder.py", LOCAL_BIN / "prompt-forge")

    # 5. Write ~/.claude/CLAUDE.md and safely merge ~/.claude/settings.json
    claude_md_target = CLAUDE_DIR / "CLAUDE.md"
    backup_path(claude_md_target)
    shutil.copy2(REPO_ROOT / "claude" / "CLAUDE.md", claude_md_target)
    print(f"  [Rules ] Wrote {claude_md_target}")
    merge_claude_settings()

    # 6. Write personal setup profile (~/.gemini/config/orchestrator_profile.json) & mentor_mode.json
    profile_data = {
        "machine_label": args.machine,
        "ram_gb": args.ram,
        "max_worktrees": max_wt,
        "account_tier": args.account_tier,
        "default_claude_model": args.default_claude_model,
        "default_architect_model": args.default_architect_model,
        "default_triage_model": "haiku",
        "default_agy_effort": "medium",
        "edit_strategy": args.edit_strategy,
    }
    profile_path = CONFIG_DIR / "orchestrator_profile.json"
    profile_path.write_text(json.dumps(profile_data, indent=2) + "\n", encoding="utf-8")
    print(f"  [Config] Saved personal setup profile to {profile_path} ({args.machine}, {args.ram}GB RAM, max {max_wt} worktrees)")

    mentor_cfg = CONFIG_DIR / "mentor_mode.json"
    mentor_enabled = args.mentor == "on"
    mentor_cfg.write_text(json.dumps({"enabled": mentor_enabled}, indent=2) + "\n", encoding="utf-8")
    print(f"  [Mentor] Set Mentor Mode = {'ON' if mentor_enabled else 'OFF'} in {mentor_cfg}")

    # 7. Ensure ~/.local/bin is in shell rc
    shell_rc = HOME / (".zshrc" if "zsh" in os.environ.get("SHELL", "zsh") else ".bashrc")
    rc_text = shell_rc.read_text(encoding="utf-8") if shell_rc.exists() else ""
    if ".local/bin" not in rc_text:
        with shell_rc.open("a", encoding="utf-8") as f:
            f.write('\nexport PATH="$HOME/.local/bin:$PATH"\n')
        print(f"  [PATH  ] Added ~/.local/bin to {shell_rc}")

    print("\nRunning `route --doctor` verification...")
    subprocess.run(["python3", str(TARGET_PLUGIN / "scripts" / "route.py"), "--doctor"], check=False)


if __name__ == "__main__":
    main()
