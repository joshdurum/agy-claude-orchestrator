---
name: build-prompt
description: Guide a novice through 2-4 simple clarifying questions to turn a rough idea into a model-perfect, cache-aligned, cost-optimized prompt for Claude, Gemini, or OpenAI using PromptForge (~/.gemini/scripts/prompt_builder.py). Use when the user runs /build-prompt or asks help crafting, optimizing, or cutting API costs on a prompt.
---

# Novice Guided Prompt Builder & API Cost Optimizer (`/build-prompt`)

Use this skill whenever the user invokes `/build-prompt` or asks to craft, structure, or reduce token/API costs for a prompt across Claude, Gemini, or OpenAI models.

## Step 1: Run Socratic Ambiguity Detection ("Clarify-Before-Compile")
1. Pass the user's rough idea to the deterministic analyzer:
   ```bash
   python3 ~/.gemini/scripts/prompt_builder.py --interview "<user's rough idea>"
   ```
2. If the user's request is missing key details (such as target stack/audience, boundaries/constraints, or output format), ask the **2–3 multiple-choice questions** returned by `--interview` (presenting the recommended default first so a beginner can simply reply *"use defaults"* or pick options).
3. If the user already specified all details or asked for an immediate prompt, proceed straight to Step 2 using the smart defaults.

## Step 2: Compile for Target Model Dialect & Calculate Cost Savings
Run `prompt_builder.py` with the gathered blocks and target model (`claude-sonnet`, `claude-opus-thinking`, `claude-haiku`, `gemini-argon-pro`, `gemini-flash`, `gemini-thinking`, `gpt-4o`, `gpt-4o-mini`, or `o3-reasoning`):
```bash
python3 ~/.gemini/scripts/prompt_builder.py "<task>"   --target-model "<model_id>"   --role "<role>"   --context "<context>"   --constraints "<constraints>"   --output-format "<output_format>"
```

## Step 3: Present the Prompt, Cost Breakdown & Beginner Walkthrough
1. **Copy-Paste Prompt Block:** Display the compiled prompt (`xml` tags for Claude, `markdown` headers for Gemini/OpenAI, or CoT-stripped specification for reasoning models).
2. **3-Layer Cost & Token Savings Summary:** Show the **First-Try Completeness Score (`0–100`)**, **Prefix-Cacheable Token %**, and the **Model Tier Cost Comparison Table** (highlighting if a budget/standard model saves 70%–90% vs. a frontier reasoning model).
3. **Beginner Walkthrough (when Mentor Mode is ON):** Explain in plain English *why* the prompt was arranged that way (e.g., why static context goes at the top for prompt caching, why XML tags help Claude separate context from instructions, and how *Chain of Draft* cuts expensive output tokens).
4. **Optional Web Studio Tip:** Mention that they can also run `route --studio` (or `prompt-forge --studio`) in Terminal anytime to open the interactive visual PromptForge Web Studio in their browser.
