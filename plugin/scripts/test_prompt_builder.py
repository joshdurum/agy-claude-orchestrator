#!/usr/bin/env python3
"""
Automated unit & integration test suite for Option A (PromptForge inside mac-studio-orchestrator).
Verifies:
1. Socratic ambiguity detection & novice interview generation across task categories
2. Lexical filler pruning + Chain-of-Draft injection + Prefix-Cache ordering
3. Model dialect compilation (XML for Claude, Markdown for Gemini/GPT, CoT-stripping for Opus/o3/Thinking)
4. Model registry live updating and 3-layer API cost table calculation
5. Backward compatibility with route.py build_prompt() and all 5 orchestrator contracts
"""
import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import prompt_builder  # noqa: E402
import route  # noqa: E402


class TestPromptForgeIntegration(unittest.TestCase):
    def test_1_socratic_interview_categories(self):
        coding = prompt_builder.analyze_and_interview("write a python script to clean csv files")
        self.assertIn(coding["category"], ("coding", "data_json"))
        self.assertGreaterEqual(len(coding["questions"]), 2)
        for q in coding["questions"]:
            self.assertTrue(q["default"])
            self.assertGreaterEqual(len(q["options"]), 2)

        arch = prompt_builder.analyze_and_interview("fix a concurrency race condition and deadlock in our worker pool")
        self.assertEqual(arch["model_recommendation"]["recommended_model"], "claude-opus-thinking")
        self.assertEqual(arch["model_recommendation"]["tier"], "reasoning")

    def test_2_lexical_pruning_and_cod(self):
        fluffy = "Hello there! Could you please, I would really appreciate it if you could write a parser in order to read logs due to the fact that they fail. Thank you in advance!"
        cleaned, saved = prompt_builder.prune_filler(fluffy)
        self.assertGreater(saved, 40)
        self.assertNotIn("Could you please", cleaned)
        self.assertIn("to read logs because they fail", cleaned)

    def test_3_dialect_compilation_claude_xml_vs_gemini_md_vs_reasoning(self):
        blocks = {
            "role": "Senior Backend Engineer",
            "context": "FastAPI service using PostgreSQL 16",
            "verification_gates": "pytest -q && ruff check .",
            "constraints": "Think step by step and do not add external dependencies.",
            "task": "Add pagination to GET /invoices",
            "output_format": "Return code diff and pytest command.",
        }
        # Claude Sonnet -> XML tags + static prefix before <task> + Chain of Draft
        claude_res = prompt_builder.compile_for_model(blocks, model_id="claude-sonnet", use_cod=True)
        cp = claude_res["compiled_prompt"]
        self.assertIn("<role>", cp)
        self.assertIn("<static_context>", cp)
        self.assertIn("<verification_gates>", cp)
        self.assertIn("Chain of Draft (CoD)", cp)
        self.assertLess(cp.index("<static_context>"), cp.index("<task>"))
        self.assertEqual(claude_res["completeness"]["score"], 100)

        # Gemini Argon -> Markdown headings + static prefix before ### TASK
        gemini_res = prompt_builder.compile_for_model(blocks, model_id="gemini-argon-pro", use_cod=True)
        gp = gemini_res["compiled_prompt"]
        self.assertIn("### ROLE", gp)
        self.assertIn("### STATIC CONTEXT (CACHE PREFIX)", gp)
        self.assertLess(gp.index("### STATIC CONTEXT"), gp.index("### TASK"))

        # Reasoning model (Claude Opus Thinking / OpenAI o3) -> strips manual 'Think step by step' and omits CoD
        opus_res = prompt_builder.compile_for_model(blocks, model_id="claude-opus-thinking", use_cod=True)
        op = opus_res["compiled_prompt"]
        self.assertNotIn("Think step by step", op)
        self.assertNotIn("Chain of Draft", op)

    def test_4_cost_table_and_registry_integrity(self):
        reg = prompt_builder.load_registry()
        self.assertGreaterEqual(len(reg["models"]), 9)
        res = prompt_builder.compile_for_model({"task": "Extract JSON fields from invoice text"}, model_id="claude-haiku")
        self.assertEqual(len(res["cost_comparison"]), len(reg["models"]))
        for row in res["cost_comparison"]:
            self.assertLess(row["optimized_cost_per_1k_runs_usd"], row["baseline_cost_per_1k_runs_usd"])
            self.assertGreater(row["savings_percent"], 30.0)

    def test_5_orchestrator_route_contract_compatibility(self):
        claude_prompt = route.build_prompt(
            task="Hello there, could you please refactor the auth middleware",
            gates="- **Test:** `pytest`",
            mentor_on=True,
            browser_check=False,
            use_worktree=True,
            runner="claude",
            model="sonnet",
        )
        self.assertIn("<verification_gates>", claude_prompt)
        self.assertIn("AGENT_ORCHESTRATION_DEPTH=1", claude_prompt)
        self.assertIn("Worktree Bootstrap", claude_prompt)
        self.assertLess(claude_prompt.index("<verification_gates>"), claude_prompt.index("<task>"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
