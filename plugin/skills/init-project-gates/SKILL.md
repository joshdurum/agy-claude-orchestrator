---
name: init-project-gates
description: Audit a repository's stack, package manager, CI workflows, worktree requirements, and test runners to generate or update project-specific Verification Gates in ./AGENTS.md and ./CLAUDE.md, explaining every tool in plain English for a beginner.
---

# Project Gate Onboarding & Migration Auditor (`/init-project-gates`)

Run this skill when opening an unconfigured project, setting up a newly cloned repo, or after migrating frameworks, package managers, or test runners.

## Step 1: Explain & Audit Repository Stack
1. **Tell the user what you are doing first:** If Mentor Mode is ON, explain in plain English that you are inspecting the project's configuration files (like `package.json` or `pyproject.toml`) to figure out what programming language, tools, and safety checks this specific project uses.
2. **Inspect the project root (without modifying source code):**
   - **Node/TS:** `package.json`, lockfiles (`bun.lock`/`bun.lockb`, `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`), `tsconfig.json`, `next.config.*`, `vite.config.*`.
   - **Python:** `pyproject.toml`, `uv.lock`, `poetry.lock`, `requirements.txt`, `pytest.ini`, `ruff.toml`.
   - **Rust / Go / Apple:** `Cargo.toml`, `go.mod`, `Package.swift`, `*.xcodeproj`, `*.xcworkspace`.
   - **Task Runners & CI:** `Makefile`, `justfile`, `.github/workflows/*.yml`, `docker-compose.yml`.
   - **Worktree Dependencies (CRITICAL):** Check if `.env`, `.env.local`, `node_modules`, or `.venv` exist in the root so fresh Git worktrees know how to copy env files or install dependencies before running tests.
3. **Identify Exact Gate Commands:**
   - **Worktree Bootstrap:** e.g., `[ -f "$MAIN/.env" ] && cp "$MAIN/.env" . ; pnpm install --frozen-lockfile` (or `"None required"` if standalone).
   - **Dev Server & URL:** e.g., `pnpm dev` at `http://localhost:3000` (for browser verification).
   - **Typecheck:** e.g., `pnpm tsc --noEmit`, `uv run mypy .`, `cargo check`.
   - **Lint / Format:** e.g., `pnpm lint`, `uv run ruff check .`, `cargo clippy -- -D warnings`.
   - **Test Suite:** e.g., `pnpm test`, `uv run pytest`, `cargo test`, `go test ./...`.
   - **Production Build:** e.g., `pnpm build`, `cargo build --release`.
   *(Omit any gate category that does not apply rather than inventing placeholder commands.)*

## Step 2: Update `./AGENTS.md` and `./CLAUDE.md`
1. **Create or Update `./AGENTS.md` (keep under 150 lines):**
   - If `./AGENTS.md` already exists, preserve all existing sections and replace (or append) only the `## Verification Gates` section.
   - If `./AGENTS.md` does not exist, create it with this structure:
     ```markdown
     # Project Instructions & Verification Gates

     ## Stack Overview
     - **Primary Stack:** <detected languages, frameworks, and package manager>
     - **Frontend / Browser Verification:** <Yes (Dev URL: http://localhost:XXXX) | No (CLI/Backend)>

     ## Verification Gates
     Run these exact commands before marking any multi-file change complete:
     - **Worktree Bootstrap:** `<command to copy .env / install deps in a fresh worktree, or "N/A">`
     - **Typecheck:** `<command>`
     - **Lint:** `<command>`
     - **Test:** `<command>`
     - **Build:** `<command>`
     - **Browser Check:** `<Dev server command + URL, or "N/A">`
     ```
2. **Ensure `./CLAUDE.md` Links to `AGENTS.md`:**
   - If `./CLAUDE.md` does not exist, create it containing `@AGENTS.md`.
   - If `./CLAUDE.md` exists and does not already include `@AGENTS.md`, prepend `@AGENTS.md` at the top of the file.

## Step 3: Beginner-Friendly Breakdown & Sanity Check
1. Walk through every file you just created or updated (`AGENTS.md` and `CLAUDE.md`).
2. When Mentor Mode is ON, explain what each detected tool and safety gate actually does in simple terms (for example, explaining that a *linter* checks code style/mistakes like a spellchecker, while a *typechecker* verifies data types match before running the app).
3. Offer to run the non-destructive gates (`Typecheck` + `Lint`) right now and explain what the output means.
