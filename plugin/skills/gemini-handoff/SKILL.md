---
name: gemini-handoff
description: Delegate high-volume code scaffolding (>5 files), boilerplate generation, or multimodal media/PDF analysis from Claude Code to Antigravity CLI (agy -p) while preventing recursion loops and respecting Mentor Mode.
---

# Global Gemini Pro Subtask Handoff (`/gemini-handoff`)

Use this skill when a subtask involves repetitive edits across >5 files, large-scale boilerplate, or analyzing images/videos/PDFs so Claude's context window stays focused on architecture and verification.

## Guardrails Before Calling
1. **Recursion Check:** If `AGENT_ORCHESTRATION_DEPTH` is `1` or higher, do **NOT** invoke `agy -p`; finish the work directly.
2. **Break-Even Check:** If the edit touches only 1–2 small files (<20 lines), do it directly instead of spawning a CLI subprocess.
3. **Inside Antigravity Check:** If you are already running inside Antigravity, use native tools (`invoke_subagent` with `self`, `research`, or `browser`) rather than shelling out to `agy -p`.

## Execution Steps (From Claude Code or Terminal)
1. Check `~/.gemini/config/mentor_mode.json` (defaults to `enabled: true` if missing).
2. Read `./AGENTS.md` (if present) to grab the current repository's `## Verification Gates`.
3. Choose `--effort high` for complex multi-file migrations or `--effort medium` for standard scaffolding/media tasks, and run:
   ```bash
   AGENT_ORCHESTRATION_DEPTH=1 agy -p "<clear task with exact file paths>. Do NOT invoke claude -p. Before finishing, run these project verification gates: <gates from ./AGENTS.md>. Return a compact digest listing: (1) every file created or modified, (2) why each change was made, and (3) the verification gate results." --effort medium --mode=auto
   ```
4. After `agy -p` exits, inspect `git diff --stat`, confirm the project's `## Verification Gates` passed, and present the summary matching the active Mentor Mode setting.
