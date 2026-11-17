---
name: cleanup-worktrees
description: Safely inspect, preserve, and remove stale Git worktrees on Mac Studio so the 36GB unified memory worktree cap (3 max) never blocks isolated tasks, explaining every step in plain English.
---

# Safe Git Worktree Cleanup (`/cleanup-worktrees`)

Use this skill when the user invokes `/cleanup-worktrees` or when `SessionStart` / `route.py` warns that 3/3 Git worktrees are active.

## Step 1: Explain & Inspect Active Worktrees
1. If Mentor Mode is ON, explain to the user in plain English that a *Git worktree* is a temporary side-folder copy of the project that lets an AI test risky multi-file changes safely without touching your main files—and cleaning up finished ones keeps your Mac Studio's 36GB memory fast.
2. Run:
   ```bash
   git worktree list
   ```
3. For each secondary worktree (**never** remove the primary main repo directory!), check if it has uncommitted changes or unmerged commits:
   ```bash
   git -C "<worktree_path>" status --short
   ```

## Step 2: Ask Before Removing Anything With Unsaved Work
- **If a secondary worktree is clean (no uncommitted changes) and already merged:** Remove it safely with `git worktree remove "<worktree_path>"` and run `git worktree prune`.
- **If a secondary worktree has uncommitted changes or unmerged commits:** Stop and explain in plain English what files were changed in that temporary copy, and ask the user whether they want to:
  1. Merge/keep those changes into their main branch first, or
  2. Discard that temporary experiment and delete the worktree.

## Step 3: Confirm New Headroom
Show the updated `git worktree list` count (`X/3`) so the user knows they are clear to keep building.
