# Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Python
Make sure Python 3.10+ is installed:
```bash
python --version
```

### Step 2: Set Up Project
```bash
# Navigate to project directory
cd diary-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run post-install for pywin32 (if needed)
python venv\Scripts\pywin32_postinstall.py -install
```

### Step 3: Configure (Optional)
Edit `config/config.json` if needed. Default settings work fine for most users.

### Step 4: Run
```bash
# Method 1: Using Python
python -m src.main

# Method 2: Using batch script (Windows)
run.bat
```

## First Run

When you start the logger, you'll see:

```
============================================================
  Workday Activity Logger v2.0.0
  Passive activity tracking for AI summarization
============================================================

Configuration: config/config.json
Output directory: logs
Polling interval: 30s
Idle timeout: 300s

Press Ctrl+C to stop...
```

## What Happens Next

1. **Logger starts polling** every 30 seconds
2. **Captures your activity**:
   - Active window (foreground)
   - Meeting apps in background (Teams, Zoom)
   - Browser URLs when possible
3. **Creates daily log** in `logs/YYYY-MM-DD_log.md`
4. **Automatically pauses** after 5 minutes of inactivity

## Viewing Logs

Open the log file:
```bash
# Open today's log
notepad logs\2026-01-28_log.md
```

Example log entry:
```markdown
| 09:30 | **Chrome**: Project Docs - [https://docs.example.com] | **Teams**: "Daily Standup" |
| 10:15 | **VS Code**: `backend/auth.py` | - |
```

## Stopping the Logger

Press `Ctrl+C` in the terminal window.

## Troubleshooting

### Common Issues

**"ImportError: No module named 'win32gui'"**
```bash
pip install pywin32
python venv\Scripts\pywin32_postinstall.py -install
```

**"Permission denied" or "Access is denied"**
- Try running terminal as Administrator
- Check antivirus isn't blocking Python

**No logs being created**
- Check `logs/` directory exists (auto-created)
- Run with `--verbose` flag to see debug info:
  ```bash
  python -m src.main --verbose
  ```

**URLs not being captured**
- Normal! UI Automation can be finicky
- Window title still captured as fallback
- Try increasing timeout in config.json

## Next Steps

1. **Customize config**: Edit `config/config.json` to:
   - Add apps to blacklist
   - Set privacy keywords
   - Adjust polling interval

2. **Use with AI**: Feed logs to ChatGPT/Claude:
   ```
   "Summarize my workday from this log: [paste log]"
   ```

3. **Automate**: Create scheduled task to run on startup

## Tips

- **Run in background**: Minimize the terminal window
- **Multiple days**: Logger automatically creates new file each day
- **Privacy**: Review `privacy_keywords` in config before sharing logs
- **Performance**: Default 30s interval is balanced; adjust if needed

## Getting Help

- Check `README.md` for full documentation
- Look at `project-brief.md` for design details
- Open an issue on GitHub (if applicable)

---

**Ready to track!** Your first activity will appear in the log after 30 seconds. 🚀
