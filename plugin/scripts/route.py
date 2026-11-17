#!/usr/bin/env python3
"""
Global Multi-Project Workflow & Smart Model Dispatcher + PromptForge Optimizer + Health Checker (--doctor)
Tailored for macOS Apple Silicon (M4 Max, 36GB RAM) & Personal Pro Accounts.
Includes:
- Stage 1 zero-token regex routing + Stage 2 fast Haiku triage
- Automatic model & effort selection (Haiku/Flash -> Sonnet -> Opus / Argon High)
- PromptForge dialect-compiled & prefix-cache-ordered prompt generation (XML for Claude, Markdown for Gemini)
- Non-destructive git stash snapshot before in-branch edits; --worktree reserved for risky multi-file refactors
- CLI flags: --optimize, --studio, --update-models, --doctor, --dry-run, --mentor, --set-mentor
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Import sibling prompt_builder module
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import prompt_builder  # noqa: E402

MAX_WORKTREES_36GB = 3
PROFILE_CFG = Path.home() / ".gemini" / "config" / "orchestrator_profile.json"


def load_profile() -> dict:
    defaults = {
        "machine_label": "Mac Studio M4 Max",
        "ram_gb": 36,
        "max_worktrees": 3,
        "account_tier": "Personal Pro (Claude + Gemini)",
        "default_claude_model": "sonnet",
        "default_architect_model": "opus",
        "default_triage_model": "haiku",
        "default_agy_effort": "medium",
        "edit_strategy": "in_branch_with_stash",
    }
    if not PROFILE_CFG.exists():
        return defaults
    try:
        return {**defaults, **json.loads(PROFILE_CFG.read_text(encoding="utf-8"))}
    except Exception:
        return defaults

MENTOR_CFG = Path.home() / ".gemini" / "config" / "mentor_mode.json"
PLUGIN_ROOT = Path.home() / ".gemini" / "config" / "plugins" / "mac-studio-orchestrator"

WORKFLOW_SPECS = {
    "agy_browser": {
        "runner": "agy",
        "model": "gemini-flash",
        "model_label": "Gemini (Default / Flash Browser Subagent)",
        "effort": "medium",
        "use_worktree": False,
        "browser_check": True,
    },
    "agy_scaffold": {
        "runner": "agy",
        "model": "gemini-argon-pro",
        "model_label": "Gemini (Argon / Medium Effort)",
        "effort": "medium",
        "use_worktree": False,
        "browser_check": False,
    },
    "claude_coding": {
        "runner": "claude",
        "model": "sonnet",
        "model_label": "Claude Sonnet (Medium Effort, In-Branch + Stash Backup)",
        "effort": "medium",
        "use_worktree": False,
        "browser_check": False,
    },
    "claude_worktree_refactor": {
        "runner": "claude",
        "model": "sonnet",
        "model_label": "Claude Sonnet (High Effort, Isolated --worktree)",
        "effort": "high",
        "use_worktree": True,
        "browser_check": False,
    },
    "claude_deep_architect": {
        "runner": "claude",
        "model": "opus",
        "model_label": "Claude Opus (High Effort, Deep Architecture / Debugging)",
        "effort": "high",
        "use_worktree": False,
        "browser_check": False,
    },
}

TRIAGE_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "workflow": {
            "type": "string",
            "enum": list(WORKFLOW_SPECS.keys()),
        },
        "reason": {"type": "string"},
    },
    "required": ["workflow", "reason"],
    "additionalProperties": False,
})

UI_PATTERN = re.compile(
    r"\b(ui|css|tailwind|layout|component|modal|browser|dom|animation|tsx|jsx|html|responsive)\b",
    re.IGNORECASE,
)
BULK_PATTERN = re.compile(
    r"\b(scaffold|boilerplate|migrate|migration|rename across|generate tests|video|audio|screenshot|pdf)\b",
    re.IGNORECASE,
)
DEEP_ARCH_PATTERN = re.compile(
    r"\b(architect|architecture|race condition|deadlock|memory leak|security audit|root cause|redesign|concurrency|distributed)\b",
    re.IGNORECASE,
)
RISKY_REFACTOR_PATTERN = re.compile(
    r"\b(refactor across|multi-file refactor|overhaul|rewrite|breaking change|database migration)\b",
    re.IGNORECASE,
)


def get_mentor_mode() -> bool:
    if not MENTOR_CFG.exists():
        return True
    try:
        return bool(json.loads(MENTOR_CFG.read_text(encoding="utf-8")).get("enabled", True))
    except Exception:
        return True


def set_mentor_mode(enabled: bool) -> None:
    MENTOR_CFG.parent.mkdir(parents=True, exist_ok=True)
    MENTOR_CFG.write_text(json.dumps({"enabled": enabled}, indent=2) + "\n", encoding="utf-8")


def check_agy_signed_in() -> bool:
    if not shutil.which("agy"):
        return False
    try:
        res = subprocess.run(["agy", "models"], capture_output=True, text=True, timeout=5)
        combined = (res.stdout + res.stderr).lower()
        return "please sign in" not in combined and res.returncode == 0
    except Exception:
        return False


def run_doctor() -> int:
    """Verify all global plugin files, PromptForge engine files, symlinks, scripts, and CLIs are healthy."""
    home = Path.home()
    checks = [
        ("Antigravity Plugin Manifest", PLUGIN_ROOT / "plugin.json"),
        ("Antigravity Plugin Rules (AGENTS.md)", PLUGIN_ROOT / "rules" / "AGENTS.md"),
        ("Antigravity Plugin SessionStart Hook", PLUGIN_ROOT / "hooks.json"),
        ("Global GEMINI.md Symlink", home / ".gemini" / "GEMINI.md"),
        ("Claude Global Rules (CLAUDE.md)", home / ".claude" / "CLAUDE.md"),
        ("Claude Settings & SessionStart Hook", home / ".claude" / "settings.json"),
        ("Session Inspector Script", home / ".gemini" / "scripts" / "session_check.py"),
        ("Mentor Mode Script", home / ".gemini" / "scripts" / "mentor.py"),
        ("Task Router Script", home / ".gemini" / "scripts" / "route.py"),
        ("PromptForge Compiler Script", home / ".gemini" / "scripts" / "prompt_builder.py"),
        ("PromptForge Model Registry", home / ".gemini" / "scripts" / "models_registry.json"),
        ("PromptForge Local Web Studio", home / ".gemini" / "scripts" / "prompt_studio.html"),
        ("Skill: /mentor-mode", PLUGIN_ROOT / "skills" / "mentor-mode" / "SKILL.md"),
        ("Skill: /init-project-gates", PLUGIN_ROOT / "skills" / "init-project-gates" / "SKILL.md"),
        ("Skill: /route-task", PLUGIN_ROOT / "skills" / "route-task" / "SKILL.md"),
        ("Skill: /build-prompt", PLUGIN_ROOT / "skills" / "build-prompt" / "SKILL.md"),
        ("Skill: /gemini-handoff", PLUGIN_ROOT / "skills" / "gemini-handoff" / "SKILL.md"),
        ("Skill: /claude-handoff", PLUGIN_ROOT / "skills" / "claude-handoff" / "SKILL.md"),
        ("Skill: /cleanup-worktrees", PLUGIN_ROOT / "skills" / "cleanup-worktrees" / "SKILL.md"),
        ("Skill: /undo-last", PLUGIN_ROOT / "skills" / "undo-last" / "SKILL.md"),
        ("Shared Claude Skills Dir", home / ".claude" / "skills"),
        ("Claude /build-prompt Symlink", home / ".claude" / "skills" / "build-prompt"),
        ("CLI Symlink: `route`", home / ".local" / "bin" / "route"),
        ("CLI Symlink: `prompt-forge`", home / ".local" / "bin" / "prompt-forge"),
    ]
    all_ok = True
    print("=== Mac Studio AI Orchestration + PromptForge Health Check ===")
    for label, path in checks:
        exists = path.exists()
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"  [{status:7}] {label}: {path}")

    for cli in ["claude", "agy", "git", "python3"]:
        found = shutil.which(cli)
        status = "OK" if found else "WARN"
        print(f"  [{status:7}] CLI `{cli}`: {found or 'not found in PATH'}")

    agy_auth = check_agy_signed_in()
    print(
        f"  [{'OK' if agy_auth else 'ACTION ':7}] `agy` CLI Auth: "
        f"{'Signed in' if agy_auth else 'Run `agy` once in Terminal to sign in for headless `agy -p` handoffs'}"
    )
    prof = load_profile()
    print(f"  [INFO   ] Hardware Profile: {prof['machine_label']} ({prof['ram_gb']}GB RAM, max {prof['max_worktrees']} worktrees, strategy={prof['edit_strategy']})")
    print(f"  [INFO   ] Mentor Mode: {'ON (Beginner Teacher)' if get_mentor_mode() else 'OFF (Standard Developer)'}")
    print("==============================================================")
    return 0 if all_ok else 1


def active_worktree_count(cwd: str) -> int:
    res = subprocess.run(
        ["git", "worktree", "list"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return 1
    return len([line for line in res.stdout.splitlines() if line.strip()])


def save_non_destructive_stash(cwd: str) -> str | None:
    """Create a git stash backup entry without reverting the working tree."""
    try:
        res = subprocess.run(
            ["git", "stash", "create", "pre-ai-handoff"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        sha = res.stdout.strip()
        if res.returncode == 0 and sha:
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            label = f"pre-ai-handoff-{ts}"
            subprocess.run(
                ["git", "stash", "store", "-m", label, sha],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            return label
    except Exception:
        pass
    return None


def read_project_gates(cwd: str) -> str | None:
    agents_path = Path(cwd) / "AGENTS.md"
    if not agents_path.exists():
        return None
    try:
        text = agents_path.read_text(encoding="utf-8")
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


def select_workflow(task: str, cwd: str, has_gates: bool) -> tuple[str, str]:
    has_agy = shutil.which("agy") is not None
    has_claude = shutil.which("claude") is not None
    if not has_claude and not has_agy:
        raise RuntimeError("Neither `claude` nor `agy` CLI was found in PATH.")

    # Stage 1: Zero-token deterministic heuristics
    if has_agy and UI_PATTERN.search(task):
        return (
            "agy_browser",
            "UI/frontend keywords detected; routing to Antigravity with browser verification.",
        )

    if has_agy and BULK_PATTERN.search(task):
        return (
            "agy_scaffold",
            "Bulk scaffolding/media task detected; routing to Gemini (Medium Effort) to preserve Claude Pro quota.",
        )

    if has_claude and DEEP_ARCH_PATTERN.search(task):
        return (
            "claude_deep_architect",
            "Deep architecture or root-cause debugging keywords detected; escalating to Claude Opus (High Effort).",
        )

    if has_claude and RISKY_REFACTOR_PATTERN.search(task):
        return (
            "claude_worktree_refactor",
            "Multi-file refactor detected; routing to Claude Sonnet (High Effort) in an isolated Git worktree.",
        )

    if not has_claude:
        return ("agy_scaffold", "Only `agy` CLI available; routing to Antigravity.")

    # Stage 2: Fast, low-cost Haiku triage with fallback to Sonnet in-branch coding
    prompt = (
        f"Classify this coding task into the best workflow and model tier. "
        f"Use `claude_coding` (in-branch Sonnet) for normal features/bugfixes, "
        f"`claude_worktree_refactor` only for risky multi-file refactors, and "
        f"`claude_deep_architect` (Opus) for complex architecture or subtle bugs. "
        f"has_project_gates={has_gates}. Task: {task}"
    )
    try:
        res = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--model",
                "haiku",
                "--effort",
                "low",
                "--output-format",
                "json",
                "--json-schema",
                TRIAGE_SCHEMA,
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=25,
            check=True,
        )
        outer = json.loads(res.stdout)
        raw_res = outer.get("result", outer.get("structured_output", outer))
        decision = json.loads(raw_res) if isinstance(raw_res, str) else raw_res
        wf = decision.get("workflow", "claude_coding")
        if wf in WORKFLOW_SPECS:
            return wf, decision.get("reason", "Selected via Stage 2 Haiku triage.")
    except Exception:
        pass

    return (
        "claude_coding",
        "Standard feature/coding task; routing to Claude Sonnet (Medium Effort) in current branch with safety backup.",
    )


def build_prompt(
    task: str,
    gates: str | None,
    mentor_on: bool,
    browser_check: bool = False,
    use_worktree: bool = False,
    runner: str = "claude",
    model: str = "sonnet",
) -> str:
    """Delegate prompt assembly to PromptForge's cache-aligned dialect compiler."""
    return prompt_builder.compile_orchestrator_prompt(
        task=task,
        gates=gates,
        mentor_on=mentor_on,
        runner=runner,
        model=model,
        browser_check=browser_check,
        use_worktree=use_worktree,
    )


def execute_workflow(
    workflow: str, task: str, cwd: str, gates: str | None, mentor_on: bool, dry_run: bool
) -> int:
    spec = WORKFLOW_SPECS[workflow]
    wt_count = active_worktree_count(cwd)
    use_worktree = spec["use_worktree"]

    if use_worktree and wt_count >= MAX_WORKTREES_36GB:
        print(
            f"[RAM Guard] {wt_count}/{MAX_WORKTREES_36GB} worktrees already active. "
            "Running in current branch after taking a non-destructive git stash backup."
        )
        use_worktree = False

    full_prompt = build_prompt(
        task,
        gates,
        mentor_on,
        browser_check=spec["browser_check"],
        use_worktree=use_worktree,
        runner=spec["runner"],
        model=spec["model"],
    )

    if spec["runner"] == "agy":
        cmd = [
            "agy",
            "-p",
            full_prompt,
            "--effort",
            spec["effort"],
            "--mode=auto",
        ]
    else:
        cmd = [
            "claude",
            "-p",
            full_prompt,
            "--model",
            spec["model"],
            "--effort",
            spec["effort"],
            "--allowedTools",
            "Read,Edit,Write,Bash",
        ]
        if use_worktree:
            cmd.insert(3, "--worktree")

    print(f"Mentor Mode: {'ON (Beginner Teacher)' if mentor_on else 'OFF (Standard Developer)'}")
    print(f"Model Tier : {spec['model_label']}")
    print(f"Dialect    : {'Anthropic XML (Cache-Aligned)' if spec['runner'] == 'claude' else 'Gemini Markdown (Cache-Aligned)'}")
    print(f"Edit Mode  : {'Isolated Git Worktree (--worktree)' if use_worktree else 'Current Branch (with automatic git stash backup)'}")
    print(f"Gates Found: {'Yes (from ./AGENTS.md)' if gates else 'No (will prompt /init-project-gates)'}")
    print(f"Command    : {' '.join(cmd[:6])} ...")
    if dry_run:
        return 0

    if not use_worktree:
        stash_label = save_non_destructive_stash(cwd)
        if stash_label:
            print(f"[Safety Net] Saved non-destructive restore point in `git stash list` as `{stash_label}`.")

    child_env = os.environ.copy()
    child_env["AGENT_ORCHESTRATION_DEPTH"] = str(int(child_env.get("AGENT_ORCHESTRATION_DEPTH", "0")) + 1)
    return subprocess.run(cmd, cwd=cwd, env=child_env).returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Global multi-project router & PromptForge optimizer for Claude Code & Antigravity.")
    parser.add_argument("task", nargs="?", help="Task description to evaluate, optimize, or execute")
    parser.add_argument("--cwd", default=".", help="Target repository directory")
    parser.add_argument("--dry-run", action="store_true", help="Print chosen workflow and model tier without executing")
    parser.add_argument("--doctor", action="store_true", help="Verify global setup files, plugin, PromptForge engine, and CLI paths")
    parser.add_argument("--optimize", action="store_true", help="Compile & cost-optimize the prompt for a target model without executing")
    parser.add_argument("--target-model", default="claude-sonnet", help="Target model ID for --optimize (default: claude-sonnet)")
    parser.add_argument("--studio", action="store_true", help="Launch the local visual PromptForge Web Studio in browser")
    parser.add_argument("--port", type=int, default=8765, help="Port for --studio (default: 8765)")
    parser.add_argument("--update-models", action="store_true", help="Display all models, dialects, and token pricing in models_registry.json")
    parser.add_argument(
        "--mentor",
        choices=["on", "off"],
        help="Override Mentor Mode for this single run without changing global setting",
    )
    parser.add_argument(
        "--set-mentor",
        choices=["on", "off"],
        help="Persistently toggle global Mentor Mode ON or OFF and exit if no task is given",
    )
    args = parser.parse_args()
    if args.doctor:
        sys.exit(run_doctor())

    if args.studio:
        prompt_builder.serve_studio(port=args.port)
        sys.exit(0)

    if args.update_models:
        reg = prompt_builder.load_registry()
        print(f"=== PromptForge Model Registry (v{reg['version']}, updated {reg['last_updated']}) ===")
        for mid, m in reg["models"].items():
            p = m["pricing_per_1m"]
            print(f"  [{m['tier']:9}] {mid:22} | {m['name']:46} | Dialect: {m['dialect']['delimiter']:8} | In: ${p['input']:.2f} (Cached: ${p['cached_input']:.2f}) / Out: ${p['output']:.2f}")
        sys.exit(0)

    if args.set_mentor:
        enabled = args.set_mentor == "on"
        set_mentor_mode(enabled)
        print(f"Global Mentor Mode saved as: {'ON' if enabled else 'OFF'}")
        if not args.task:
            sys.exit(0)

    if not args.task:
        parser.error("the following arguments are required: task (unless using --doctor, --studio, --update-models, or --set-mentor)")

    if args.optimize:
        cwd = os.path.abspath(args.cwd)
        gates = read_project_gates(cwd) or ""
        report = prompt_builder.compile_for_model(
            blocks={"task": args.task, "verification_gates": gates},
            model_id=args.target_model,
            use_cod=True,
        )
        print(f"=== PromptForge Optimized Prompt ({report['target_model']['name']}) ===")
        print(f"First-Try Completeness : {report['completeness']['score']}/100")
        print(f"Prefix Cacheable Ratio : {report['token_metrics']['prefix_cache_ratio_pct']}%")
        print(f"Smart Tier Advice      : {report['model_recommendation']['recommended_model']} — {report['model_recommendation']['why']}")
        print("\n--- COMPILED PROMPT ---")
        print(report["compiled_prompt"])
        print("-----------------------\n")
        print("Estimated Cost per 1,000 Runs (Unoptimized Retry Baseline vs. PromptForge):")
        for row in report["cost_comparison"][:5]:
            print(
                f"  [{row['tier']:9}] {row['id']:20}: ${row['baseline_cost_per_1k_runs_usd']:6.2f} -> "
                f"${row['optimized_cost_per_1k_runs_usd']:6.2f} ({row['savings_percent']}% saved)"
            )
        sys.exit(0)

    mentor_on = (args.mentor == "on") if args.mentor else get_mentor_mode()
    cwd = os.path.abspath(args.cwd)
    gates = read_project_gates(cwd)
    workflow, reason = select_workflow(args.task, cwd, has_gates=gates is not None)
    print(f"Selected Workflow: {workflow}\nReason: {reason}")
    sys.exit(execute_workflow(workflow, args.task, cwd, gates, mentor_on, args.dry_run))


if __name__ == "__main__":
    main()
