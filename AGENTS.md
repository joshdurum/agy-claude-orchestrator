# Project Instructions & Verification Gates (`agy-claude-orchestrator`)

## Stack Overview
- **Primary Stack:** Python 3.10+ (standard library only, zero external dependencies), Bash, HTML5/JS (PromptForge Studio)
- **Frontend / Browser Verification:** Yes (`python3 plugin/scripts/prompt_builder.py --studio` at `http://127.0.0.1:8765`)

## Verification Gates
Run these exact commands before marking any multi-file change complete:
- **Worktree Bootstrap:** `N/A (zero external dependencies)`
- **Typecheck / Syntax Compile:** `python3 -m py_compile install.py uninstall.py plugin/scripts/*.py`
- **Lint / JSON Schema Validation:** `jq . plugin/plugin.json plugin/hooks.json plugin/scripts/models_registry.json profile.example.json > /dev/null`
- **Test:** `python3 plugin/scripts/test_prompt_builder.py`
- **Build / Dry-Run Check:** `python3 plugin/scripts/route.py --dry-run "Build a responsive settings modal"`
