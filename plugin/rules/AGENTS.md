# Global Workspace Orchestration & Gate Policy (Mac Studio M4 Max)

## 1. Communication Style: Toggleable Mentor Mode (`~/.gemini/config/mentor_mode.json`)
Always check the Mentor Mode status injected by `SessionStart` (or read `~/.gemini/config/mentor_mode.json`; defaults to `ON` if unset). The user can flip this switch anytime using `/mentor-mode`.

- **When Mentor Mode is ON (Beginner Learning Mode):**
  1. **Treat the user as a beginner learning while building:** Never assume prior knowledge of developer jargon. Whenever you use a technical term (such as *linter*, *worktree*, *dependency*, *endpoint*, *state*, *schema*, or *hook*), briefly define what it means in plain English.
  2. **Explain before acting:** Clearly state what you are about to do, which files or commands you are going to touch, and *why* this step is necessary.
  3. **Explain after acting:** Walk through what you just changed step-by-step. Translate the code or terminal commands into plain English and explain the core programming concepts behind them so the user understands how and why the solution works.
  4. **Teach progressively:** Use clear formatting, bullet points, and real-world analogies when introducing new concepts, and invite questions before jumping into major changes.
- **When Mentor Mode is OFF (Standard Developer Mode):**
  1. Skip beginner definitions, analogies, and pre-action narration.
  2. Execute tasks directly and provide concise, high-signal technical summaries of modified files, key architectural choices, and verification gate results.

## 2. Hardware, Account & Loop-Safety Profile
- **Machine:** macOS Apple Silicon (M4 Max, 36GB Unified Memory).
- **Accounts:** Personal Pro (Claude & Gemini). Both `claude` and `agy` CLIs have full OAuth and `--mode=auto` privileges.
- **Concurrency Cap:** Never exceed **3 active Git worktrees** simultaneously across a repository to preserve unified memory headroom alongside VS Code, Antigravity, and Chrome DevTools. If 3 worktrees are active, guide the user to run `/cleanup-worktrees` or work in the current branch.
- **Anti-Recursion Guard (`AGENT_ORCHESTRATION_DEPTH`):** If `AGENT_ORCHESTRATION_DEPTH` is set to `1` or higher in the environment, **do NOT** call `claude -p` or `agy -p` again. Complete the assigned subtask directly to prevent infinite agent-to-agent ping-pong loops.
- **Break-Even Delegation Rule:** Do **NOT** spawn an external agent CLI for tiny single-file edits (<20 lines). Only delegate when a task genuinely benefits from specialized strengths (>5 files of boilerplate, multimodal media/PDF analysis, deep architectural design, or complex multi-file refactors).

## 3. Smart Model & Effort Selection Policy
When routing or delegating tasks between Antigravity and Claude Code, automatically match the model and reasoning effort to the task's complexity:
- **Fast Triage (`route.py` Stage 2):** `claude -p --model haiku --effort low` (only when deterministic Stage 1 heuristics do not match).
- **Visual / UI / DOM Inspection:** Inside Antigravity, use the native `browser` subagent (`Model: "flash"`) for live Chrome inspection; from Claude Code or Terminal, invoke `agy -p --mode=auto --effort medium`.
- **High-Volume Scaffolding (>5 files) & Media/PDF Analysis:** `agy -p --mode=auto --effort medium` (leverages Gemini's large context window and preserves Claude Pro 5-hour quota).
- **Standard Feature Implementation & Bug Fixes:** `claude -p --model sonnet --effort medium` running in the current branch (after taking a non-destructive `git stash` snapshot).
- **Risky Multi-File Refactors:** `claude -p --worktree --model sonnet --effort high` in an isolated Git worktree.
- **Deep Architecture & Hard Root-Cause Debugging:** `claude -p --model opus --effort high` (adds `--worktree` if making risky multi-file changes).

- **Guided Prompt Building & API Cost Optimization (`/build-prompt` / `prompt-forge`):** Whenever the user wants to craft a high-precision prompt, reduce API token spend, or adapt a prompt across Claude (XML), Gemini (Markdown), or OpenAI/Reasoning models, use `/build-prompt` (backed by `~/.gemini/scripts/prompt_builder.py` and `~/.gemini/scripts/models_registry.json`, or `route --studio` for the local visual Web Studio).

## 4. Automatic Per-Project Gate Onboarding
- Every code repository must define its project-specific build, lint, typecheck, test, dev-server, and worktree bootstrap commands under `## Verification Gates` in its root `AGENTS.md` (keep `AGENTS.md` concise—under 150 lines).
- If the `SessionStart` hook reports that a project lacks `## Verification Gates` in `AGENTS.md` (or if the user states they just migrated or restructured the project), run `/init-project-gates` before making code edits to inspect the repo's manifests and generate tailored gate commands.
- Never mark a multi-file task complete until the project's `## Verification Gates` commands pass cleanly.

## 5. Compact Digest & Safety Guardrails
- **Compact Digest Contract:** Whenever delegating to another agent CLI, require a structured summary (changed files + diff stat + gate results + beginner walkthrough if Mentor Mode is ON)—never dump raw multi-thousand-line file contents back into context.
- **Beginner Safety Guardrails:** Never run destructive commands (`rm -rf`, `git push --force`, `git reset --hard`) or overwrite `.env` secret files without explicit user confirmation.
