@~/.gemini/GEMINI.md

# Claude Code Global Specifics

1. **Toggleable Mentor Mode (`~/.gemini/config/mentor_mode.json`):** Check `~/.gemini/config/mentor_mode.json` (defaults to `enabled: true` if missing; toggled via `/mentor-mode`).
   - If `enabled` is `true`: Treat the user as a beginner learning while building—explain what you are doing and why before every action, walk through every file change and command in plain English afterward, define jargon, and teach underlying programming concepts.
   - If `enabled` is `false`: Use Standard Developer Mode—execute directly and report concise technical summaries without beginner narration.
2. **Anti-Recursion Guard:** If `AGENT_ORCHESTRATION_DEPTH` is `1` or higher, never invoke `agy -p` or `claude -p`; complete the task directly in this session.
3. **Project Gates & `AGENTS.md`:** Always read the current repository's root `AGENTS.md` (imported via `@AGENTS.md` in project `CLAUDE.md`) and run every command under `## Verification Gates` before finishing a task. If missing, run `/init-project-gates` first.
4. **Edit Strategy & Worktree Bootstrap Rule:**
   - For standard coding tasks, edit in the current branch (after saving a non-destructive `git stash` backup if dirty).
   - Reserve `--worktree` for risky multi-file refactors (when active worktrees are `< 3`). Inside a fresh Git worktree, run the project's `## Worktree Bootstrap` command from `AGENTS.md` before running tests.
   - Keep `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` disabled by default. Use `/gemini-handoff` for bulk scaffolding across >5 files or media/PDF inspection.
