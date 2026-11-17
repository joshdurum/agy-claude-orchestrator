# Antigravity + Claude Code Orchestrator & PromptForge

A zero-dependency, multi-project orchestration plugin and cost-optimizing prompt compiler that connects **Google Antigravity (`agy` / IDE / 2.0)** and **Anthropic Claude Code (`claude`)** into a single seamless workflow.

Built originally for a **Mac Studio (M4 Max, 36GB RAM)** and designed so **any developer or beginner can customize it to their own hardware, RAM limits, model preferences, and learning style in one command.**

---

## What It Does

1. **Automatic Task & Model Tier Routing (`/route-task` & `route` CLI):**
   - **Tiny Edits (`<20` lines):** Runs directly in your active agent with zero subprocess startup delay.
   - **Frontend / UI / DOM Verification:** Routes to **Antigravity** (`Gemini Flash` native `browser` subagent + `Argon`) to inspect live Chrome rendering and console logs.
   - **Bulk Scaffolding (`>5` files) & Multimodal Media/PDFs:** Routes to **Antigravity (`agy -p --effort medium --mode=auto`)** to leverage Gemini's context window and save your Claude 5-hour session quota.
   - **Standard Coding & Bug Fixes:** Routes to **Claude Sonnet (`claude -p --model sonnet --effort medium`)** in your current branch after taking an automatic, non-destructive `git stash` restore point.
   - **Risky Multi-File Refactors:** Routes to **Claude Sonnet (`claude -p --worktree --model sonnet --effort high`)** in an isolated Git worktree (automatically capped to match your system RAM).
   - **Deep Architecture & Root-Cause Debugging:** Escalates to **Claude Opus (`claude -p --model opus --effort high`)**.
2. **PromptForge Guided Builder & 3-Layer API Cost Optimizer (`/build-prompt`, `prompt-forge`, `route --studio`):**
   - **Socratic Ambiguity Detection:** Turns rough ideas into 2–3 multiple-choice clarifying questions with smart defaults—eliminating 3–4 costly retry turns.
   - **Prefix-Cache Structural Ordering:** Places static Role, Context, and Verification Gates at the top prefix (`50%–90%` cached input token discount) and dynamic task inputs at the bottom.
   - **Chain of Draft (`<=5` words/step) & Dialect Compilation:** Compiles **XML tags** for Claude, **Markdown sections** for Gemini/OpenAI, and automatically strips manual Chain-of-Thought for native Reasoning models (`Opus High`, `Gemini Thinking`, `OpenAI o3`).
   - **Local Visual Web Studio:** Zero-dependency browser app at `http://127.0.0.1:8765` (`route --studio`).
3. **Automatic Per-Project Safety Gates (`SessionStart` Hook + `/init-project-gates`):**
   - Whenever you open a repository in Antigravity or Claude Code, `session_check.py` checks if `./AGENTS.md` has custom `## Verification Gates` (Typecheck, Lint, Test, Build, Worktree Bootstrap) and prompts `/init-project-gates` if missing.
4. **Toggleable Beginner Mentor Mode (`/mentor-mode`):**
   - Flip between **Beginner Teacher Mode (`ON`)** (defines jargon in plain English and explains every action before and after taking it) and **Standard Developer Mode (`OFF`)** (concise technical digests) across both AIs at once.

---

## Quick Start (1-Minute Install)

### Prerequisites
- **macOS** or **Linux** (or Windows WSL2)
- **Python 3.10+** (`python3 --version`) and **Git** (`git --version`)
- **Claude Code CLI** (`claude`) and/or **Google Antigravity** (`agy` CLI / Antigravity Desktop)

### Default Install (36GB Mac Studio Profile)
```bash
git clone https://github.com/<your-github-username>/agy-claude-orchestrator.git
cd agy-claude-orchestrator
./install.sh
source ~/.zshrc
```

---

## How to Customize It for Your Personal Setup

Every user has different hardware, memory limits, subscription tiers, and workflow preferences. You can customize your setup **during installation** via CLI flags or **anytime afterward** by editing `~/.gemini/config/orchestrator_profile.json`.

### 1. Customize for Your Machine & RAM (`--machine`, `--ram`, `--max-worktrees`)
Each isolated Git worktree (`claude --worktree`) can spawn its own language server, compiler cache, or test runner. The installer automatically calculates a safe concurrency cap from your `--ram` (or lets you set `--max-worktrees` directly):

| Your Machine / RAM | Recommended Install Command | Worktree Cap |
| :--- | :--- | :--- |
| **16GB MacBook Air / Pro** | `./install.sh --machine "MacBook Pro 16GB" --ram 16` | `1` max worktree |
| **24GB MacBook Air / Mini** | `./install.sh --machine "Mac Mini M4 24GB" --ram 24` | `2` max worktrees |
| **36GB–48GB Mac Studio / Pro** | `./install.sh --machine "Mac Studio M4 Max" --ram 36` | `3` max worktrees |
| **64GB–128GB Workstation** | `./install.sh --machine "Mac Studio 128GB" --ram 128 --max-worktrees 6` | `6` max worktrees |

### 2. Customize Your Edit Strategy & Default Models
- **Prefer Experienced Developer Mode by default (no beginner explanations)?**
  ```bash
  ./install.sh --mentor off
  ```
  *(You can still toggle it anytime in chat with `/mentor-mode on` or `/mentor-mode off`.)*
- **Prefer *every* Claude handoff to use an isolated Git worktree instead of editing in-branch with a `git stash` backup?**
  ```bash
  ./install.sh --edit-strategy always_worktree
  ```
- **Prefer Opus for all coding tasks (or Sonnet for everything to conserve quota)?**
  ```bash
  ./install.sh --default-claude-model sonnet --default-architect-model opus
  ```

### 3. Customize Model Dialects & Token Pricing (`models_registry.json`)
PromptForge reads all model rules and pricing from `~/.gemini/scripts/models_registry.json`:
- **From the Browser UI:** Run `route --studio` and use the **Updatable Model Rulebook** card to add new prompting rules with one click.
- **From Terminal:**
  ```bash
  # View all registered models, dialects, and token prices
  route --update-models

  # Add a custom prompting rule to any model
  prompt-forge --add-rule claude-sonnet "Always wrap file paths in <filepath> tags."
  ```

### 4. Editing Your Profile JSON Directly (`~/.gemini/config/orchestrator_profile.json`)
See [`profile.example.json`](./profile.example.json) for all supported keys:
```json
{
  "machine_label": "Mac Studio M4 Max",
  "ram_gb": 36,
  "max_worktrees": 3,
  "account_tier": "Personal Pro (Claude + Gemini)",
  "default_claude_model": "sonnet",
  "default_architect_model": "opus",
  "default_triage_model": "haiku",
  "default_agy_effort": "medium",
  "edit_strategy": "in_branch_with_stash",
  "mentor_mode_default": true
}
```

---

## Included Slash Commands (Active in Both Antigravity & Claude Code)

| Command | What It Does |
| :--- | :--- |
| `/build-prompt <idea>` | Runs the guided Socratic interview, compresses tokens, orders blocks for prompt caching, compiles into XML/Markdown, and shows API cost savings. |
| `/route-task <task>` | Analyzes your repo gates, active worktrees, and task complexity to pick and run the optimal AI + model tier. |
| `/init-project-gates` | Audits your repo (`package.json`, `pyproject.toml`, `Cargo.toml`, `.env`, CI) and generates `## Verification Gates` in `./AGENTS.md` and `./CLAUDE.md`. |
| `/mentor-mode [on\|off]` | Flips Beginner Mentor & Learning Mode ON or OFF globally across both Antigravity and Claude Code. |
| `/claude-handoff` | Passes backend coding (`sonnet`), multi-file refactors (`sonnet --worktree`), or deep architecture (`opus`) from Antigravity to Claude Code. |
| `/gemini-handoff` | Offloads `>5`-file boilerplate generation or PDF/image/video analysis from Claude Code to Antigravity (`agy -p`). |
| `/undo-last` | Saves a safety backup in `git stash` and cleanly rolls back recent uncommitted AI edits. |
| `/cleanup-worktrees` | Inspects secondary Git worktrees for unsaved work and prunes finished ones to keep memory free. |

---

## Terminal CLI Commands

```bash
# Run the 29-point health check across Antigravity, Claude Code, and PromptForge
route --doctor

# Preview which AI, model tier, and dialect a task will use without running it
route --dry-run "Investigate concurrency race condition in worker pool"

# Compile & cost-optimize any prompt for Claude, Gemini, or OpenAI
route --optimize "Write a Python script to parse PDF invoices into JSON" --target-model claude-sonnet

# Launch the local visual PromptForge Web Studio at http://127.0.0.1:8765
route --studio
```

---

## Safe Backups & Uninstalling

- **Non-Destructive Install:** `install.py` backs up any existing files to `~/.gemini/backups/<timestamp>/` and **merges** its `SessionStart` hook into `~/.claude/settings.json` without overwriting your existing Claude model settings, theme, or other skills.
- **Uninstall Anytime:**
  ```bash
  python3 uninstall.py
  ```

## For AI Agents Merging or Auditing This Repo
Read [`AI_README.md`](./AI_README.md) for the complete symlink topology, `SessionStart` JSON schemas, anti-recursion invariants, and the **Option A / B / C Merge Decision Matrix**.
