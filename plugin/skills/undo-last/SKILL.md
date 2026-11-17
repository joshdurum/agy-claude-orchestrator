---
name: undo-last
description: Beginner-friendly safety net to inspect recent uncommitted AI edits and cleanly roll them back (with a backup git stash) if something went wrong.
---

# Beginner Safe Undo (`/undo-last`)

Use this skill whenever the user invokes `/undo-last` or says something like *"undo what the AI just changed"* or *"go back to how it was before."*

## Step 1: Explain & Show What Changed First
1. Reassure the user in plain English that nothing is permanently lost—you will first show them which files changed and save a hidden safety backup (*Git stash*) before reverting anything.
2. Run:
   ```bash
   git status --short && git diff --stat && git stash list -n 5
   ```
3. Explain in plain English which files were modified or newly created, and note if there is also a recent `pre-ai-handoff-*` or `pre-claude-handoff-*` snapshot in `git stash list`.

## Step 2: Save a Safety Backup & Revert (After Confirming)
Ask the user to confirm rolling back the current uncommitted changes. Once confirmed:
1. Create a named safety backup stash (including untracked files) so even the undo can be undone:
   ```bash
   git stash push -u -m "pre-undo-backup-$(date +%Y%m%d-%H%M%S)"
   ```
2. Walk the user through what happened in plain English: their project files are now back to their clean state, and a safety backup was tucked away in `git stash list` (`git stash pop` can bring it right back if they ever want it).
