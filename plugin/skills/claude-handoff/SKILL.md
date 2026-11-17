---
name: claude-handoff
description: Automatically delegate backend coding, tricky debugging, deep architecture, or isolated multi-file refactors from Antigravity (Argon) to Claude Code CLI (claude -p) with automatic Sonnet vs. Opus model selection and git stash safety backups.
---

# Claude Code Subtask Handoff (`/claude-handoff`)

Use this skill whenever Antigravity (Argon) determines a task benefits from Claude Code's execution, deep architectural reasoning, or isolated worktree refactoring.

## Step 1: Check Recursion, Complexity Tier & Safety Backup
1. **Recursion Check:** If `AGENT_ORCHESTRATION_DEPTH` is `1` or higher, do **NOT** invoke `claude -p`; complete the task directly.
2. **Break-Even Check:** For tiny single-file edits (<20 lines), execute directly in Antigravity instead of spawning Claude Code.
3. **Select Model & Edit Mode Automatically:**
   - **Standard Coding / Bug Fix (`--model sonnet --effort medium`, current branch):** Default for normal multi-file features, unit tests, and bug fixes. Before invoking `claude -p`, save a non-destructive stash restore point if the repo has uncommitted changes:
     ```bash
     stash_sha=$(git stash create "pre-claude-handoff") && [ -n "$stash_sha" ] && git stash store -m "pre-claude-handoff-$(date +%Y%m%d-%H%M%S)" "$stash_sha"
     ```
   - **Deep Architecture / Root-Cause Debugging (`--model opus --effort high`, current branch):** Use when the task involves complex system design, race conditions, security audits, or subtle bugs.
   - **Risky Multi-File Refactor (`--worktree --model sonnet --effort high` or `--model opus --effort high`):** Reserve `--worktree` for sweeping, risky refactors across many files when `git worktree list` shows fewer than 3 active worktrees.

## Step 2: Choose Hands-Free vs. Guided Handoff

### Default — Hands-Free Automatic Pass (90% of cases)
When the goal is clear and self-contained, invoke Claude Code headlessly with `AGENT_ORCHESTRATION_DEPTH=1` (or run `~/.local/bin/route "<task>"`):
```bash
AGENT_ORCHESTRATION_DEPTH=1 claude -p "<clear goal, target file paths, what Argon already checked, and acceptance criteria>. Do NOT invoke agy -p. Before finishing, run these project verification gates from ./AGENTS.md: <gates>. Return a compact digest with: (1) every file changed and why, (2) key programming concepts used (if Mentor Mode is ON), and (3) verification gate results."   --model <sonnet|opus>   --effort <medium|high>   --allowedTools "Read,Edit,Write,Bash"
```
*(Add `--worktree` only for risky multi-file refactors when active worktrees < 3, and instruct Claude to commit its verified changes to the worktree branch and report the branch name so you can merge it back cleanly.)*

When Claude finishes, inspect `git diff --stat` and present the results matching the current Mentor Mode setting (`~/.gemini/config/mentor_mode.json`).

### Guided Interactive Pass (10% of cases — When User Should Steer Live)
If the task is open-ended or requires live back-and-forth design choices from the user:
1. Tell the user clearly: **"Open the Claude Code panel in VS Code (or Terminal) and paste the message below:"**
2. Provide a single, self-contained prompt block containing:
   - The goal, exact file paths, recommended model (`/model sonnet` or `/model opus`), and findings so far
   - A reminder to follow `@AGENTS.md` verification gates
   - If Mentor Mode is ON, include: *"Please treat me as a beginner who is learning while building—explain every action you take before and after doing it, define any technical terms, and teach me the concepts behind your changes."*
