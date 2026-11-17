---
name: route-task
description: Analyze the current repository scope, project verification gates, active git worktrees, and task complexity on Mac Studio (M4 Max 36GB) to recommend and initiate the optimal Antigravity vs. Claude Code workflow and model tier.
---

# Global Task & Model Router (`/route-task`)

When the user invokes `/route-task` or asks which workflow or model to use for the current task:

## Step 1: Inspect Workspace State
1. If Mentor Mode is ON, tell the user briefly that you are checking the project's safety gates and active Git worktrees so you can pick the best tool and model tier for the job.
2. Check if `./AGENTS.md` has a `## Verification Gates` section. If missing, run `/init-project-gates` first.
3. Run `~/.local/bin/route --dry-run "<task description>"` (or inspect `git status --short` and `git worktree list`) to preview the recommended route and model tier:
   - **Tiny Edit (<20 lines):** Execute directly in the current agent (0 spawn overhead).
   - **Option A — Antigravity UI + Native `browser` Subagent (`flash` + Argon):** Best for visual/UI work, checking layouts live in Chrome, or multimodal inspection.
   - **Option B — Antigravity Bulk Scaffolding (`agy -p --mode=auto --effort medium`):** Best when generating boilerplate across >5 files or analyzing PDFs/videos/images while saving Claude Pro quota.
   - **Option C — Claude Code Standard Coding (`claude -p --model sonnet --effort medium`):** Edits directly in the current branch after saving a non-destructive `git stash` restore point. Best for standard backend features, tests, and bug fixes.
   - **Option D — Claude Code Isolated Worktree Refactor (`claude -p --worktree --model sonnet --effort high`):** Creates an isolated temporary worktree (`< 3` cap) for risky multi-file refactors.
   - **Option E — Claude Code Deep Architect (`claude -p --model opus --effort high`):** Escalates to Claude Opus with high reasoning effort for complex system architecture, concurrency bugs, or tricky root-cause debugging.

## Step 2: Execute with Verification Gates
Once confirmed (or immediately if the user asked you to proceed), execute the chosen workflow, explain each step according to the active Mentor Mode setting, and run the project's `## Verification Gates` at the end.
