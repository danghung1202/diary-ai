# 🚀 Get Started in 3 Minutes

## ✅ What You Got

A complete **Workday Activity Logger** that:
- ✅ Tracks your computer activity automatically
- ✅ Captures browser URLs, app usage, and meeting context
- ✅ Creates AI-friendly Markdown logs
- ✅ Protects your privacy
- ✅ Runs silently in the background

## 📦 Installation

### Option 1: Automatic (Recommended)

**Double-click**: `install.bat`

That's it! The script will:
- Check Python installation
- Create virtual environment
- Install all dependencies
- Configure everything

### Option 2: Manual

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## ▶️ Run the Logger

### Option 1: Quick Start

**Double-click**: `run.bat`

### Option 2: Manual

```bash
# Activate virtual environment
venv\Scripts\activate

# Run the logger
python -m src.main
```

You'll see:

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

## 📊 View Your Logs

After a few minutes, check your logs:

```bash
# Open today's log
notepad logs\2026-01-28_log.md
```

You'll see a nice table:

| Time | Activity Description (Focus) | Background Context |
| --- | --- | --- |
| 09:30 | **Chrome**: Documentation - [https://docs.example.com] | **Teams**: "Daily Standup" |
| 10:00 | **VS Code**: `src/main.py` | - |
| 10:30 | **Terminal**: `git commit -m "Update"` | - |

## 🎯 Use with AI

### Daily Stand-up

Copy your log and paste into ChatGPT/Claude:

```
Summarize my workday from this log as a stand-up update:

[paste your log here]
```

### Timesheet

```
Create a timesheet from this activity log, grouping by project:

[paste your log here]
```

### Productivity Analysis

```
Analyze my productivity patterns and suggest improvements:

[paste your log here]
```

## ⚙️ Customize (Optional)

Edit `config/config.json`:

```json
{
  "polling_interval_seconds": 30,        // How often to check
  "idle_timeout_seconds": 300,           // When to pause (5 min)
  "blacklist_processes": [               // Apps to ignore
    "Spotify.exe",
    "WhatsApp.exe"
  ],
  "privacy_keywords": [                  // Words to redact
    "password",
    "bank"
  ]
}
```

## 🛑 Stop the Logger

Press `Ctrl+C` in the terminal window.

## 📚 Learn More

- **README.md** - Full documentation
- **QUICKSTART.md** - Detailed quick start
- **ARCHITECTURE.md** - Technical architecture
- **PROJECT_SUMMARY.md** - Implementation details

## 🔧 Troubleshooting

### "Python not found"
Install Python 3.10+ from https://www.python.org/

### "ImportError: No module named 'win32gui'"
Run:
```bash
pip install pywin32
python venv\Scripts\pywin32_postinstall.py -install
```

### "No logs appearing"
1. Run with verbose: `python -m src.main --verbose`
2. Check `logs/` folder was created
3. Wait 30 seconds for first poll

### "URLs not captured"
Normal! UI Automation can be finicky. The window title is still captured as a fallback.

## 💡 Pro Tips

1. **Run on Startup**: Create Windows Task Scheduler task
2. **Background Mode**: Minimize the terminal window
3. **Weekly Review**: Use AI to summarize entire week
4. **Privacy First**: Review `privacy_keywords` before sharing logs

## 🎉 You're Ready!

The logger is running and tracking your activity every 30 seconds.

Your first log entry will appear after:
- ✅ 30 seconds (first poll)
- ✅ You're actively using the computer
- ✅ Activity changes from last poll

**Enjoy effortless activity tracking! 🎊**

---

## Quick Command Reference

| Command | Purpose |
|---------|---------|
| `install.bat` | Install everything |
| `run.bat` | Start the logger |
| `python -m src.main` | Start (manual) |
| `python -m src.main --verbose` | Start with debug info |
| `Ctrl+C` | Stop the logger |
| `notepad logs\YYYY-MM-DD_log.md` | View logs |

---

**Questions?** Check the documentation files or review the code comments.
