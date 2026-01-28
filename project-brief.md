# PROJECT BRIEF: Workday Activity Logger (Final)

**Project Name:** Workday Activity Logger (CLI)
**Version:** 2.0 (Consolidated)
**Date:** January 28, 2026
**Role:** Business Analyst
**Status:** **Ready for Development**

## 1. Executive Summary

The "Workday Activity Logger" is a headless, command-line interface (CLI) tool for Windows designed to passively record user activity. Unlike standard time-trackers, it is optimized for **AI summarization**. It employs a **"Hybrid" collection strategy**—using lightweight polling for general apps and targeted UI automation for browsers—to generate a high-fidelity Markdown journal. This ensures that multitasking (e.g., researching during a meeting) and context (e.g., specific URLs) are captured without user intervention.

## 2. Problem Statement

* **The Gap:** Knowledge workers struggle to recall specific context (URLs, file names, meeting topics) when generating daily stand-ups or timesheets.
* **The Failure of Current Tools:** Manual logging is high-friction and often abandoned. Automatic screen recorders are privacy-invasive and produce video data that is hard for LLMs to parse textually.
* **The Need:** A "Text-First" logger that produces structured data specifically formatted for Large Language Models to read and summarize.

## 3. Functional Requirements

### 3.1 The "Dual-Track" Logging Engine

To accurately capture multitasking, the system must record two distinct layers of activity simultaneously:

1. **Foreground Focus (The "Hand"):** The window currently receiving keyboard/mouse input (e.g., Chrome, VS Code).
2. **Background Context (The "Ear"):** Specific communication apps (Teams, Zoom, Meet) running in the background that indicate passive participation (e.g., a meeting).

### 3.2 The "Strategy Pattern" Data Collection

The tool must treat applications differently based on their value, balancing data richness with system performance:

* **Strategy A: Deep Inspection (Browsers)**
* *Target:* Chrome, Edge.
* *Action:* Use UI Automation to extract the **Active URL** from the address bar.


* **Strategy B: Developer Context (Tools)**
* *Target:* VS Code, Terminal, PowerShell.
* *Action:* Capture the **Window Title** (often contains filename or command) but *skip* UI Automation to save CPU.


* **Strategy C: Generic Fallback**
* *Target:* All other apps (Notepad, Explorer).
* *Action:* Capture Process Name + Window Title.



### 3.3 Noise Control

* **Idle Detection:** Logging must pause if no mouse/keyboard input is detected for >5 minutes (configurable).
* **Blacklist:** Ability to ignore specific process names (e.g., `Spotify.exe`, `WhatsApp.exe`) to keep the log professional.

## 4. Technical Specification

### 4.1 System Architecture

* **Language:** Python 3.10+
* **Platform:** Windows 10/11
* **Key Libraries:**
* `pywin32` (Win32 API access for window handles).
* `uiautomation` (For extracting URLs from browser address bars).
* `psutil` (For process enumeration).
* `pynput` (For monitoring global input idle time).



### 4.2 Logic Flow (The Polling Loop)

*Interval: Every 30 seconds*

1. **Check Idle:** Is `CurrentTime - LastInputTime > 300s`?
* *Yes:* Log `[IDLE]` and sleep.
* *No:* Proceed.


2. **Get Foreground Window:** Identify the active process.
3. **Execute Strategy:**
* IF Browser -> Fetch URL + Title.
* IF Other -> Fetch Title only.


4. **Scan Background:**
* Check list of running windows for "Meeting Whitelist" (Zoom/Teams).
* IF found -> Extract Meeting Title.


5. **Write Output:** Append to Markdown file.

### 4.3 Data Schema (`YYYY-MM-DD_log.md`)

The output is a Markdown table designed for LLM ingestion.

| Time | Activity Description (Focus) | Background Context |
| --- | --- | --- |
| 09:00 | **Outlook**: Inbox - "Project Alpha Requirements" | - |
| 09:30 | **Chrome**: [suspicious link removed] | **Teams**: "Daily Standup" |
| 10:15 | **VS Code**: `backend/auth.py` | **Teams**: "Daily Standup" |
| 11:00 | **Terminal**: `npm install` | - |

## 5. Risks & Mitigation

| Risk | Impact | Mitigation |
| --- | --- | --- |
| **Performance Lag** | UI Automation can be slow (200ms+) on some apps. | **Strict Timeout:** If URL fetch takes >0.5s, abort and use Title only. Cache window handles. |
| **Privacy Leak** | Logging sensitive URLs (e.g., password reset links). | **User Blacklist:** Config file to exclude domains or window titles containing specific keywords (e.g., "Bank", "Password"). |
| **Data Bloat** | Log file becomes too large. | **Deduplication:** Only write a new line if the Focus or Context has *changed* since the last poll. |

---
