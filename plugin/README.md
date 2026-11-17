# Mac Studio AI Orchestrator (`mac-studio-orchestrator`)

Global multi-project orchestration bundle connecting **Antigravity (Argon)** and **Claude Code** on macOS Apple Silicon (M4 Max, 36GB RAM).

## Included Customizations
- **Global Rules (`rules/AGENTS.md` + `~/.gemini/GEMINI.md` + `~/.claude/CLAUDE.md`):** Enforces toggleable Beginner Mentor Mode, 3-worktree RAM cap, `AGENT_ORCHESTRATION_DEPTH=1` loop prevention, `<20`-line break-even rule, per-project `## Verification Gates`, and automatic model/effort tiering.
- **SessionStart Lifecycle Hook (`hooks.json` + `scripts/session_check.py`):** Inspects the active workspace on session start, reports Mentor Mode and Git worktree headroom (`X/3`), and alerts when `./AGENTS.md` is missing `## Verification Gates`.
- **Smart CLI Dispatcher (`scripts/route.py` / `~/.local/bin/route`):**
  - Stage 1 zero-token regex heuristics + Stage 2 fast Haiku triage (`--model haiku --effort low`).
  - Auto-selects **Sonnet (`medium`)** for standard coding in the current branch (with automatic non-destructive `git stash` snapshot), **Sonnet (`high` + `--worktree`)** for risky multi-file refactors, **Opus (`high`)** for deep architecture/debugging, and **Antigravity (`agy -p` / `browser` subagent)** for UI verification, bulk scaffolding, and media inspection.
- **7 Shared Skills (active in both Antigravity and Claude Code):**
  - `/mentor-mode` — Toggle Beginner Mentor & Learning Mode (`ON`/`OFF`/`status`).
  - `/init-project-gates` — Audit any repo's stack and generate custom `## Verification Gates` in `./AGENTS.md` and `./CLAUDE.md`.
  - `/route-task` — Recommend and launch the optimal workflow and model tier for any task.
  - `/claude-handoff` — Hand off backend/refactoring/architectural tasks from Antigravity to Claude Code (`sonnet` or `opus`).
  - `/gemini-handoff` — Hand off >5-file scaffolding or media/PDF tasks from Claude Code to Antigravity (`agy -p`).
  - `/cleanup-worktrees` — Safely inspect and prune finished Git worktrees (`<= 3` cap).
  - `/undo-last` — Save a safety stash backup and cleanly revert recent AI edits.
