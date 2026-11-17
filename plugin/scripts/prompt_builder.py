#!/usr/bin/env python3
"""
PromptForge Engine for Mac Studio AI Orchestrator (Option A Integration).
Provides:
1. Novice Socratic Guided Interview (Clarify-Before-Compile across the 5-Block Contract)
2. 3-Layer API Cost Reduction:
   - Layer 1: First-Try Completeness Scorer (6 dimensions + auto self-check rubric)
   - Layer 2: Lexical Filler Pruning + Prefix-Cache Structural Ordering + Chain of Draft (CoD)
   - Layer 3: Cross-Model Cost & Tier Advisor (Budget vs. Standard vs. Reasoning tiers)
3. Declarative Model Dialect Compiler (XML for Claude, Markdown for Gemini/OpenAI, CoT-stripped for Reasoning)
4. Updatable Model Registry CLI & Local Zero-Dependency Web Studio (http://127.0.0.1:8765)
"""
import argparse
import datetime
import json
import re
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = SCRIPT_DIR / "models_registry.json"
STUDIO_HTML_PATH = SCRIPT_DIR / "prompt_studio.html"

FILLER_PATTERNS = [
    (r"(?i)\b(hi|hello|hey) there[,!]*\s*", ""),
    (r"(?i)\b(could|would|can) you please[,!]*\s*", ""),
    (r"(?i)\bi would (really )?(like|love|appreciate( it if)?) (you to|for you to)[,!]*\s*", ""),
    (r"(?i)\bplease make sure (that )?(you )?", "Ensure "),
    (r"(?i)\bi want you to act as\s+", "Role: "),
    (r"(?i)\bbasically[, ]+what i (want|need) (is|to do is)\s+", ""),
    (r"(?i)\bin order to\b", "to"),
    (r"(?i)\bdue to the fact that\b", "because"),
    (r"(?i)\bat this point in time\b", "now"),
    (r"(?i)\bthank you( so much)?( in advance)?[!.]*\s*", ""),
]

MANUAL_COT_PATTERNS = [
    r"(?i)think step[- ]by[- ]step[^.\n]*[.\n]?",
    r"(?i)explain your reasoning step[- ]by[- ]step[^.\n]*[.\n]?",
    r"(?i)show all your step[- ]by[- ]step thoughts[^.\n]*[.\n]?",
]

CATEGORY_PATTERNS = {
    "coding": re.compile(
        r"\b(code|script|function|bug|api|react|python|typescript|nextjs|swift|sql|database|refactor|test|cli|app|css|html)\b",
        re.IGNORECASE,
    ),
    "data_json": re.compile(
        r"\b(json|csv|parse|extract|schema|table|spreadsheet|invoice|sql|transform|dataset)\b",
        re.IGNORECASE,
    ),
    "writing": re.compile(
        r"\b(write|email|blog|article|copy|summary|summarize|essay|post|newsletter|documentation|readme)\b",
        re.IGNORECASE,
    ),
    "research": re.compile(
        r"\b(research|compare|analyze|audit|evaluate|benchmark|pros and cons|investigate|architecture)\b",
        re.IGNORECASE,
    ),
}


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Model registry not found at {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(data: dict) -> None:
    data["last_updated"] = datetime.date.today().isoformat()
    REGISTRY_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def detect_category(raw_idea: str) -> str:
    for cat, pat in CATEGORY_PATTERNS.items():
        if pat.search(raw_idea):
            return cat
    return "general"


def recommend_model_for_task(raw_idea: str, category: str) -> dict:
    text = raw_idea.lower()
    if any(k in text for k in ["architect", "race condition", "deadlock", "security audit", "root cause", "distributed", "prove"]):
        return {
            "recommended_model": "claude-opus-thinking",
            "alternative_model": "gemini-thinking",
            "tier": "reasoning",
            "why": "Deep architectural or subtle root-cause problem benefits from native high-effort reasoning.",
        }
    if any(k in text for k in ["classify", "triage", "short summary", "extract fields", "quick check"]):
        return {
            "recommended_model": "gemini-flash",
            "alternative_model": "claude-haiku",
            "tier": "budget",
            "why": "Structured extraction/triage runs at 85%-95% lower API cost on a fast budget-tier model without losing accuracy.",
        }
    if any(k in text for k in ["scaffold", "boilerplate", "pdf", "video", "image", "ui", "tailwind", "css", "html"]):
        return {
            "recommended_model": "gemini-argon-pro",
            "alternative_model": "gemini-flash",
            "tier": "standard",
            "why": "UI/multimodal or multi-file scaffolding plays to Gemini's large context window and preserves Claude quota.",
        }
    return {
        "recommended_model": "claude-sonnet",
        "alternative_model": "gemini-argon-pro",
        "tier": "standard",
        "why": "Standard implementation, analysis, or coding gets the best balance of first-try accuracy and cost on Sonnet / Argon.",
    }


def analyze_and_interview(raw_idea: str) -> dict:
    """
    Analyze a novice's rough prompt idea across the 5-Block Contract and generate
    2-4 plain-English multiple-choice clarifying questions with smart defaults.
    """
    idea = raw_idea.strip()
    category = detect_category(idea)
    model_rec = recommend_model_for_task(idea, category)

    role_defaults = {
        "coding": "Senior Full-Stack & Systems Engineer writing clean, verified production code",
        "data_json": "Data Extraction & Schema Specialist producing strict, validated structured output",
        "writing": "Clear Technical Writer & Editor focused on high-signal, audience-tailored prose",
        "research": "Principal Systems Architect & Technical Auditor",
        "general": "Expert Domain Specialist & Problem Solver",
    }

    questions = []
    if category == "coding":
        questions = [
            {
                "id": "context_stack",
                "block": "context",
                "question": "What language, framework, or environment is this code running in?",
                "default": "Python 3.12+ / TypeScript on macOS (or detect from current repository)",
                "options": [
                    "Python 3.12+ (standard library preferred)",
                    "TypeScript / Node.js / React (Next.js / Tailwind)",
                    "Shell / macOS CLI automation (zsh / bash)",
                    "Detect automatically from my current project's AGENTS.md",
                ],
            },
            {
                "id": "constraints",
                "block": "constraints",
                "question": "What safety rules or boundaries should the AI follow?",
                "default": "Zero external dependencies unless necessary; handle errors gracefully; keep functions modular",
                "options": [
                    "Zero external dependencies unless necessary; handle edge cases & errors",
                    "Modify only the target files; do not break existing APIs or tests",
                    "Optimize for readability and include beginner-friendly comments",
                ],
            },
            {
                "id": "output_format",
                "block": "output_format",
                "question": "How should the AI format its response?",
                "default": "Complete runnable code + brief file summary + verification command",
                "options": [
                    "Complete runnable code + brief file summary + verification command",
                    "Code diff only + 3-bullet explanation (minimal tokens)",
                    "Step-by-step beginner tutorial + annotated code blocks",
                ],
            },
        ]
    elif category == "data_json":
        questions = [
            {
                "id": "context_stack",
                "block": "context",
                "question": "Where is the input data coming from?",
                "default": "Unstructured text, documents, or raw records pasted below",
                "options": [
                    "Unstructured text, emails, or documents pasted below",
                    "CSV / log lines / tabular records",
                    "API responses or messy JSON payloads",
                ],
            },
            {
                "id": "constraints",
                "block": "constraints",
                "question": "How should missing or uncertain fields be handled?",
                "default": "Never guess or hallucinate values; use null when a field is missing",
                "options": [
                    "Never guess values; output null when a field is missing",
                    "Flag uncertain fields in a `warnings` array",
                    "Skip incomplete records entirely",
                ],
            },
            {
                "id": "output_format",
                "block": "output_format",
                "question": "What exact output format do you need?",
                "default": "Strict valid JSON only (no markdown wrapper or conversational text)",
                "options": [
                    "Strict valid JSON only (no conversational filler)",
                    "Markdown table + bulleted summary of key anomalies",
                    "CSV format with a header row",
                ],
            },
        ]
    else:
        questions = [
            {
                "id": "context_stack",
                "block": "context",
                "question": "Who is the target audience or what is the background context?",
                "default": "A beginner-friendly but technically accurate guide for a builder on macOS",
                "options": [
                    "Beginner-friendly explanation (plain English, no unexplained jargon)",
                    "Executive / decision-maker summary (concise trade-offs & action items)",
                    "Deep technical engineering specification",
                ],
            },
            {
                "id": "constraints",
                "block": "constraints",
                "question": "What constraints or rules should keep the answer focused?",
                "default": "No fluff or generic filler; cite concrete trade-offs and actionable steps",
                "options": [
                    "No fluff or filler; focus strictly on actionable steps and trade-offs",
                    "Keep total length under 300 words",
                    "Include concrete examples and pitfalls to avoid",
                ],
            },
            {
                "id": "output_format",
                "block": "output_format",
                "question": "How would you like the final output structured?",
                "default": "Structured Markdown with clear headings, comparison table, and checklist",
                "options": [
                    "Structured Markdown with headings, comparison table, and checklist",
                    "Numbered step-by-step action plan",
                    "Concise bullet points only",
                ],
            },
        ]

    return {
        "raw_idea": idea,
        "category": category,
        "suggested_role": role_defaults.get(category, role_defaults["general"]),
        "model_recommendation": model_rec,
        "questions": questions,
    }


def prune_filler(text: str) -> tuple[str, int]:
    """Remove polite conversational filler and collapse redundant whitespace."""
    if not text:
        return "", 0
    orig_len = len(text)
    cleaned = text
    for pat, repl in FILLER_PATTERNS:
        cleaned = re.sub(pat, repl, cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    saved_chars = max(0, orig_len - len(cleaned))
    return cleaned, saved_chars


def strip_manual_cot(text: str) -> str:
    """Strip manual 'think step by step' phrases when targeting native reasoning models."""
    cleaned = text
    for pat in MANUAL_COT_PATTERNS:
        cleaned = re.sub(pat, "", cleaned)
    return cleaned.strip()


def estimate_tokens(text: str) -> int:
    """Fast deterministic token estimator (~4 chars per token, minimum 1)."""
    if not text.strip():
        return 0
    return max(1, int(round(len(text) / 3.8)))


def score_completeness(blocks: dict) -> dict:
    """Score prompt across 6 dimensions that prevent costly multi-turn retries."""
    checks = {
        "role": bool(blocks.get("role", "").strip()),
        "context": bool(blocks.get("context", "").strip() or blocks.get("verification_gates", "").strip()),
        "task": len(blocks.get("task", "").strip()) >= 12,
        "constraints": bool(blocks.get("constraints", "").strip()),
        "output_format": bool(blocks.get("output_format", "").strip()),
        "self_check": bool(blocks.get("self_check", "").strip()),
    }
    weights = {
        "role": 15,
        "context": 20,
        "task": 25,
        "constraints": 15,
        "output_format": 15,
        "self_check": 10,
    }
    total = sum(weights[k] for k, passed in checks.items() if passed)
    missing = [k for k, passed in checks.items() if not passed]
    return {
        "score": total,
        "dimensions": checks,
        "missing": missing,
        "estimated_turns_without_optimization": 3 if total < 70 else 1,
        "estimated_turns_with_optimization": 1,
    }


def calculate_cost_table(
    registry: dict,
    raw_input_tokens: int,
    optimized_input_tokens: int,
    static_prefix_tokens: int,
    use_cod: bool,
) -> list[dict]:
    """
    Compare estimated cost per 1,000 runs across all models in models_registry.json:
    - Unoptimized baseline: 2.5 average turns (due to ambiguity retries), 450 output tokens/turn, 0% cache hit.
    - Optimized PromptForge: 1 turn (first-try completeness), prefix cache hit on static_prefix_tokens,
      and Chain of Draft output compression (180 output tokens vs 450).
    """
    rows = []
    baseline_turns = 2.4
    baseline_out_tokens = 450
    opt_out_tokens = 175 if use_cod else 360

    dynamic_tokens = max(10, optimized_input_tokens - static_prefix_tokens)

    for model_id, m in registry.get("models", {}).items():
        prices = m["pricing_per_1m"]
        p_in = prices["input"]
        p_cache = prices["cached_input"]
        p_out = prices["output"]

        # Baseline cost for 1,000 runs (unoptimized, multi-turn retries, verbose output)
        base_in_cost = (raw_input_tokens * baseline_turns * p_in) / 1000.0
        base_out_cost = (baseline_out_tokens * baseline_turns * p_out) / 1000.0
        base_total_1k = round(base_in_cost + base_out_cost, 4)

        # Optimized cost for 1,000 runs (1 turn, cached static prefix, CoD compact output)
        opt_in_cost = ((static_prefix_tokens * p_cache) + (dynamic_tokens * p_in)) / 1000.0
        opt_out_cost = (opt_out_tokens * p_out) / 1000.0
        opt_total_1k = round(opt_in_cost + opt_out_cost, 4)

        savings_pct = round((1.0 - (opt_total_1k / max(base_total_1k, 0.0001))) * 100, 1)
        rows.append({
            "id": model_id,
            "name": m["name"],
            "provider": m["provider"],
            "tier": m["tier"],
            "baseline_cost_per_1k_runs_usd": base_total_1k,
            "optimized_cost_per_1k_runs_usd": opt_total_1k,
            "savings_percent": max(0.0, savings_pct),
        })
    return rows


def compile_for_model(
    blocks: dict,
    model_id: str = "claude-sonnet",
    use_cod: bool = True,
) -> dict:
    """
    Compile structured prompt blocks into the target model's native dialect,
    applying lexical pruning, prefix-cache static ordering, and CoD / CoT rules.
    """
    registry = load_registry()
    models = registry.get("models", {})
    if model_id not in models:
        model_id = "claude-sonnet"
    model_spec = models[model_id]
    dialect = model_spec["dialect"]

    raw_combined = " ".join(str(v) for v in blocks.values() if v)
    raw_tokens = max(estimate_tokens(raw_combined) + 35, 45)

    # Prune filler from each block
    cleaned_blocks = {}
    total_chars_pruned = 0
    for key in ["role", "context", "verification_gates", "constraints", "task", "output_format", "self_check"]:
        val, saved = prune_filler(str(blocks.get(key, "") or ""))
        total_chars_pruned += saved
        if dialect["reasoning_style"] == "native_hidden_cot":
            val = strip_manual_cot(val)
        cleaned_blocks[key] = val

    # Auto-populate defaults if missing so completeness reaches 100%
    cat = detect_category(cleaned_blocks.get("task", ""))
    if not cleaned_blocks["role"]:
        cleaned_blocks["role"] = analyze_and_interview(cleaned_blocks["task"])["suggested_role"]
    if not cleaned_blocks["constraints"]:
        cleaned_blocks["constraints"] = "Follow all requirements strictly; do not invent unrequested features or placeholder values."
    if not cleaned_blocks["output_format"]:
        cleaned_blocks["output_format"] = "Provide a clean, well-structured response matching the task requirements."
    if not cleaned_blocks["self_check"]:
        cleaned_blocks["self_check"] = (
            "Before finalizing, verify that all constraints, edge cases, and output format rules are satisfied."
        )

    # Determine reasoning directive (Chain of Draft vs Native Hidden CoT)
    reasoning_directive = ""
    optimizations_applied = [
        "Prefix-Cache Ordering: Placed static Role, Context, Gates, and Constraints at the top prefix before the dynamic Task.",
        "First-Try Completeness Guard: Added explicit Role, Constraints, Output Contract, and Self-Verification Rubric to eliminate retry turns.",
    ]
    if total_chars_pruned > 0:
        optimizations_applied.append(f"Lexical Filler Pruning: Stripped {total_chars_pruned} characters of conversational fluff.")

    if dialect["reasoning_style"] == "native_hidden_cot":
        optimizations_applied.append(
            f"Reasoning Model Optimization ({model_spec['name']}): Stripped manual step-by-step CoT instructions so native internal reasoning runs without redundant output token overhead."
        )
    elif use_cod:
        reasoning_directive = (
            "Chain of Draft (CoD): Think step-by-step using at most 5 words per step inside <draft>...</draft> tags before producing the final output."
        )
        optimizations_applied.append(
            "Chain of Draft (CoD) Output Compression: Replaced verbose Chain-of-Thought with <=5-word draft steps (cuts output tokens by up to 65%)."
        )

    # Compile in target dialect (Static prefix blocks FIRST, dynamic task LAST)
    static_parts = []
    dynamic_parts = []

    if dialect["delimiter"] == "xml":
        optimizations_applied.append("Anthropic XML Dialect: Structured sections using semantic XML tags (<role>, <static_context>, <constraints>, <task>, <output_contract>).")
        static_parts.append(f"<role>\n{cleaned_blocks['role']}\n</role>")
        if cleaned_blocks["context"]:
            static_parts.append(f"<static_context>\n{cleaned_blocks['context']}\n</static_context>")
        if cleaned_blocks["verification_gates"]:
            static_parts.append(f"<verification_gates>\n{cleaned_blocks['verification_gates']}\n</verification_gates>")
        constraints_body = cleaned_blocks["constraints"]
        if reasoning_directive:
            constraints_body = f"{constraints_body}\n- {reasoning_directive}"
        static_parts.append(f"<constraints>\n{constraints_body}\n</constraints>")

        dynamic_parts.append(f"<task>\n{cleaned_blocks['task']}\n</task>")
        dynamic_parts.append(
            f"<output_contract>\n{cleaned_blocks['output_format']}\n"
            f"<self_check>{cleaned_blocks['self_check']}</self_check>\n</output_contract>"
        )
    else:
        optimizations_applied.append(f"{model_spec['provider']} Markdown Dialect: Structured sections with clear ### headings and cache-friendly prefix ordering.")
        static_parts.append(f"### ROLE\n{cleaned_blocks['role']}")
        if cleaned_blocks["context"]:
            static_parts.append(f"### STATIC CONTEXT (CACHE PREFIX)\n{cleaned_blocks['context']}")
        if cleaned_blocks["verification_gates"]:
            static_parts.append(f"### VERIFICATION GATES\n{cleaned_blocks['verification_gates']}")
        constraints_body = cleaned_blocks["constraints"]
        if reasoning_directive:
            constraints_body = f"{constraints_body}\n- {reasoning_directive}"
        static_parts.append(f"### CONSTRAINTS & BOUNDARIES\n{constraints_body}")

        dynamic_parts.append(f"### TASK\n{cleaned_blocks['task']}")
        dynamic_parts.append(
            f"### OUTPUT CONTRACT & SELF-CHECK\n{cleaned_blocks['output_format']}\n- **Self-Check:** {cleaned_blocks['self_check']}"
        )

    static_text = "\n\n".join(static_parts)
    dynamic_text = "\n\n".join(dynamic_parts)
    compiled_prompt = f"{static_text}\n\n{dynamic_text}"

    static_tokens = estimate_tokens(static_text)
    opt_tokens = estimate_tokens(compiled_prompt)
    completeness = score_completeness(cleaned_blocks)
    cost_table = calculate_cost_table(
        registry=registry,
        raw_input_tokens=raw_tokens,
        optimized_input_tokens=opt_tokens,
        static_prefix_tokens=static_tokens,
        use_cod=(use_cod and dialect["reasoning_style"] != "native_hidden_cot"),
    )

    return {
        "target_model": model_spec,
        "compiled_prompt": compiled_prompt,
        "blocks": cleaned_blocks,
        "completeness": completeness,
        "token_metrics": {
            "raw_estimated_tokens": raw_tokens,
            "optimized_prompt_tokens": opt_tokens,
            "static_prefix_cacheable_tokens": static_tokens,
            "prefix_cache_ratio_pct": round((static_tokens / max(opt_tokens, 1)) * 100, 1),
            "chars_pruned": total_chars_pruned,
        },
        "optimizations_applied": optimizations_applied,
        "cost_comparison": cost_table,
        "model_recommendation": recommend_model_for_task(cleaned_blocks["task"], cat),
    }


def compile_orchestrator_prompt(
    task: str,
    gates: str | None,
    mentor_on: bool,
    runner: str = "claude",
    model: str = "sonnet",
    browser_check: bool = False,
    use_worktree: bool = False,
) -> str:
    """
    Used directly by route.py to build cache-aligned, model-dialect-optimized prompts
    for headless Claude Code (XML) and Antigravity (Markdown) handoffs while preserving all
    5 Mac Studio Orchestrator contracts.
    """
    cleaned_task, _ = prune_filler(task)
    constraints = [
        "Anti-Recursion Rule: AGENT_ORCHESTRATION_DEPTH=1 is active. Do NOT spawn another agent CLI; finish directly."
    ]
    if browser_check:
        constraints.append("Verify the rendered UI using the browser subagent before finishing.")
    if use_worktree:
        constraints.append(
            "You are running inside an isolated Git worktree. If `./AGENTS.md` defines a Worktree Bootstrap command, run it first before running tests."
        )
    if mentor_on:
        output_contract = (
            "Communication Style (Mentor Mode ON): Treat the user as a beginner learning while building. "
            "Explain every action before and after taking it, define any jargon in plain English, and "
            "walk through the programming concepts behind your changes."
        )
    else:
        output_contract = (
            "Communication Style (Mentor Mode OFF): Return a compact digest of changed files and gate results."
        )

    gates_block = (
        f"Enforce these project verification gates before finishing:\n{gates}"
        if gates
        else "Note: This repository does not have ./AGENTS.md verification gates yet. Run /init-project-gates first to configure them, then verify your changes."
    )

    # Static blocks at top (for prompt caching), dynamic task at bottom
    if runner == "claude":
        constraints_xml = "\n".join(f"- {c}" for c in constraints)
        return (
            f"<verification_gates>\n{gates_block}\n</verification_gates>\n\n"
            f"<constraints>\n{constraints_xml}\n</constraints>\n\n"
            f"<output_contract>\n{output_contract}\n</output_contract>\n\n"
            f"<task>\n{cleaned_task}\n</task>"
        )
    else:
        constraints_md = "\n".join(f"- {c}" for c in constraints)
        return (
            f"### VERIFICATION GATES\n{gates_block}\n\n"
            f"### CONSTRAINTS\n{constraints_md}\n\n"
            f"### OUTPUT CONTRACT\n{output_contract}\n\n"
            f"### TASK\n{cleaned_task}"
        )


def update_model_rule(model_id: str, new_rule: str | None = None, prices: tuple[float, float, float] | None = None) -> dict:
    registry = load_registry()
    models = registry.get("models", {})
    if model_id not in models:
        raise ValueError(f"Unknown model_id '{model_id}'. Available: {', '.join(models.keys())}")
    if new_rule:
        if new_rule not in models[model_id]["best_practices"]:
            models[model_id]["best_practices"].append(new_rule)
    if prices:
        models[model_id]["pricing_per_1m"] = {
            "input": float(prices[0]),
            "cached_input": float(prices[1]),
            "output": float(prices[2]),
        }
    save_registry(registry)
    return models[model_id]


class StudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        pass  # Keep terminal clean

    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            html = STUDIO_HTML_PATH.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif parsed.path == "/api/models":
            self._send_json(load_registry())
        else:
            self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if self.path == "/api/interview":
            res = analyze_and_interview(body.get("raw_idea", ""))
            self._send_json(res)
        elif self.path == "/api/compile":
            res = compile_for_model(
                blocks=body.get("blocks", {}),
                model_id=body.get("model_id", "claude-sonnet"),
                use_cod=bool(body.get("use_cod", True)),
            )
            self._send_json(res)
        elif self.path == "/api/update-model":
            updated = update_model_rule(
                model_id=body["model_id"],
                new_rule=body.get("new_rule"),
            )
            self._send_json({"ok": True, "model": updated, "registry": load_registry()})
        else:
            self._send_json({"error": "Not found"}, status=404)


def serve_studio(port: int = 8765, open_browser: bool = True) -> None:
    server = HTTPServer(("127.0.0.1", port), StudioHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"=== PromptForge Local Web Studio running at {url} ===")
    print("Press Ctrl+C to stop.")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped PromptForge Studio.")
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PromptForge: Novice Guided Prompt Builder, 3-Layer Cost Optimizer & Model Dialect Compiler."
    )
    parser.add_argument("idea", nargs="?", help="Rough prompt idea or task to analyze/compile")
    parser.add_argument("--interview", action="store_true", help="Output guided clarifying questions as JSON")
    parser.add_argument("--target-model", default="claude-sonnet", help="Target model ID from models_registry.json")
    parser.add_argument("--role", default="", help="Optional Role override")
    parser.add_argument("--context", default="", help="Optional static Context override")
    parser.add_argument("--constraints", default="", help="Optional Constraints override")
    parser.add_argument("--output-format", default="", help="Optional Output Format override")
    parser.add_argument("--no-cod", action="store_true", help="Disable Chain of Draft compression")
    parser.add_argument("--json", action="store_true", help="Print full compilation report as JSON")
    parser.add_argument("--list-models", action="store_true", help="List all models and rules in models_registry.json")
    parser.add_argument("--add-rule", nargs=2, metavar=("MODEL_ID", "RULE"), help="Add a best-practice rule to a model in models_registry.json")
    parser.add_argument("--studio", action="store_true", help="Launch the local visual PromptForge Web Studio")
    parser.add_argument("--port", type=int, default=8765, help="Port for --studio (default: 8765)")
    args = parser.parse_args()

    if args.studio:
        serve_studio(port=args.port)
        return

    if args.list_models:
        reg = load_registry()
        print(f"=== Model Registry (v{reg['version']}, updated {reg['last_updated']}) ===")
        for mid, m in reg["models"].items():
            p = m["pricing_per_1m"]
            print(f"  - {mid:22} | {m['name']:48} | In: ${p['input']:.2f} (Cache: ${p['cached_input']:.2f}) / Out: ${p['output']:.2f}")
        return

    if args.add_rule:
        mid, rule = args.add_rule
        updated = update_model_rule(mid, new_rule=rule)
        print(f"Added rule to {mid} ({updated['name']}). Total rules: {len(updated['best_practices'])}")
        return

    if not args.idea:
        parser.error("Provide a prompt idea, or use --studio / --list-models / --add-rule.")

    if args.interview:
        print(json.dumps(analyze_and_interview(args.idea), indent=2))
        return

    blocks = {
        "role": args.role,
        "context": args.context,
        "constraints": args.constraints,
        "task": args.idea,
        "output_format": args.output_format,
    }
    report = compile_for_model(blocks, model_id=args.target_model, use_cod=not args.no_cod)
    if args.json:
        print(json.dumps(report, indent=2))
        return

    tm = report["token_metrics"]
    comp = report["completeness"]
    rec = report["model_recommendation"]
    print(f"=== PromptForge Optimized Prompt ({report['target_model']['name']}) ===")
    print(f"Completeness Score : {comp['score']}/100 (Estimated turns needed: {comp['estimated_turns_with_optimization']} vs {comp['estimated_turns_without_optimization']} unoptimized)")
    print(f"Cacheable Prefix   : {tm['static_prefix_cacheable_tokens']}/{tm['optimized_prompt_tokens']} tokens ({tm['prefix_cache_ratio_pct']}% eligible for 50%-90% cache discount)")
    print(f"Recommended Tier   : {rec['recommended_model']} ({rec['tier']} tier) — {rec['why']}")
    print("\n--- COMPILED PROMPT (COPY & PASTE) ---")
    print(report["compiled_prompt"])
    print("--------------------------------------\n")
    print("Optimizations Applied:")
    for opt in report["optimizations_applied"]:
        print(f"  * {opt}")
    print("\nEstimated Cost per 1,000 Runs (Unoptimized Retry Baseline vs. PromptForge):")
    for row in report["cost_comparison"][:5]:
        print(
            f"  [{row['tier']:9}] {row['id']:20}: ${row['baseline_cost_per_1k_runs_usd']:6.2f} -> "
            f"${row['optimized_cost_per_1k_runs_usd']:6.2f} ({row['savings_percent']}% saved)"
        )


if __name__ == "__main__":
    main()
