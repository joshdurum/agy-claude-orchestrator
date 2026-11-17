---
name: mentor-mode
description: Toggle Beginner Mentor & Learning Mode ON or OFF globally across Antigravity and Claude Code by updating ~/.gemini/config/mentor_mode.json. Use when the user runs /mentor-mode or asks to turn beginner explanations on or off.
---

# Toggle Beginner Mentor & Learning Mode (`/mentor-mode`)

Use this skill whenever the user runs `/mentor-mode` (with optional `on`, `off`, `toggle`, or `status`) or asks to turn beginner explanations on or off.

## Step 1: Run `~/.gemini/scripts/mentor.py`
Determine which action the user asked for:
- If the user said `/mentor-mode on` or asked to turn beginner/mentor mode on -> pass `on`
- If the user said `/mentor-mode off` or asked for concise/developer mode -> pass `off`
- If the user asked whether mentor mode is on -> pass `status`
- If the user just typed `/mentor-mode` with no argument -> pass `toggle`

Execute:
```bash
python3 ~/.gemini/scripts/mentor.py <on|off|toggle|status>
```

## Step 2: Confirm & Immediately Adopt the New Mode
- **If `MENTOR_MODE=ON`:** Confirm in warm, beginner-friendly language that **Beginner Mentor & Learning Mode is now ON**. Explain briefly that from this moment forward, both Antigravity (Argon) and Claude Code will define technical terms, explain every action before and after taking it, and teach programming concepts as you build—and remind them they can type `/mentor-mode off` anytime to switch to concise mode.
- **If `MENTOR_MODE=OFF`:** Confirm concisely in 1–2 sentences that **Beginner Mentor Mode is now OFF (Standard Developer Mode active)**. Switch immediately to crisp, high-signal technical summaries while continuing to enforce all `## Verification Gates`. Remind them they can type `/mentor-mode on` anytime to bring back step-by-step teaching.
