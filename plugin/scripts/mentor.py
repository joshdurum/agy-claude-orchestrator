#!/usr/bin/env python3
"""
Deterministic Mentor Mode switcher shared across Antigravity (Argon) and Claude Code.
Stores state in ~/.gemini/config/mentor_mode.json (defaults to ON for beginners).
"""
import argparse
import json
from pathlib import Path

CFG_PATH = Path.home() / ".gemini" / "config" / "mentor_mode.json"


def read_state() -> bool:
    if not CFG_PATH.exists():
        return True
    try:
        return bool(json.loads(CFG_PATH.read_text(encoding="utf-8")).get("enabled", True))
    except Exception:
        return True


def write_state(enabled: bool) -> None:
    CFG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CFG_PATH.write_text(json.dumps({"enabled": enabled}, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Toggle or query global Mentor Mode.")
    parser.add_argument(
        "action",
        nargs="?",
        default="toggle",
        choices=["on", "off", "toggle", "status"],
        help="Action to perform (default: toggle)",
    )
    args = parser.parse_args()
    current = read_state()
    if args.action == "status":
        print(f"MENTOR_MODE={'ON' if current else 'OFF'}")
        return

    if args.action == "on":
        new_state = True
    elif args.action == "off":
        new_state = False
    else:
        new_state = not current

    write_state(new_state)
    print(f"MENTOR_MODE={'ON' if new_state else 'OFF'}")


if __name__ == "__main__":
    main()
