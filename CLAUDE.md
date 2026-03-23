# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Workday Activity Logger v2.0 — a Windows-only CLI tool that passively records user computer activity (browser URLs, window focus, meetings) and outputs daily Markdown logs optimized for LLM summarization. Runs headlessly in the background with a 30-second polling loop.

## Commands

```bash
# Install
pip install -r requirements.txt
python venv\Scripts\pywin32_postinstall.py -install

# Run
python -m src.main                     # Default config
python -m src.main --verbose           # Debug logging
python -m src.main --config path.json  # Custom config
run.bat                                # Quick-start (activates venv + --verbose)

# Test
pytest tests/
```

## Architecture

**Coordinator pattern**: `ActivityLogger` orchestrates all components in a single-threaded polling loop (pynput idle listeners run on background threads).

**Polling cycle** (every 30s):
1. `IdleDetector` — check idle via pynput mouse/keyboard listeners
2. `WindowDetector` — get foreground window (Win32 API) + scan background for meetings
3. `StrategyFactory` → selects `BrowserStrategy` / `DeveloperToolsStrategy` / `GenericStrategy` based on process name
4. `PrivacyFilter` — redact sensitive keywords/URLs
5. `ActivityDeduplicator` — skip if state unchanged
6. `MarkdownWriter` — append row to daily log file (`logs/YYYY-MM-DD_log.md`)

**Strategy pattern** (`src/strategies/`):
- `BrowserStrategy` — extracts URLs via `uiautomation` (Chrome/Edge/Firefox address bar) with 0.5s timeout, falls back to window title
- `DeveloperToolsStrategy` — parses VS Code/Terminal window titles for filenames/commands
- `GenericStrategy` — fallback returning process name + window title

**Key dataclasses**: `WindowInfo` (from WindowDetector), `ActivityInfo` (from strategies).

## Platform Constraints

- **Windows 10/11 only** — depends on pywin32, uiautomation, Win32 API
- Config lives in `config/config.json` with hardcoded defaults as fallback
- Output is Markdown tables — pipe characters in content must be escaped (replaced with dashes) to prevent table corruption

## Known Gotchas

- `BrowserStrategy` uses UI Automation which can be slow/flaky — always has a timeout fallback
- Meeting detection filters by both process name whitelist AND window title heuristics (must contain meeting-related keywords, not just chat windows)
- The foreground window must be excluded from background meeting scanning to avoid duplicate entries
