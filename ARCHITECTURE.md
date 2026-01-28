# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                            │
│                          (main.py)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Activity Logger                               │
│                 (Polling Coordinator)                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             Polling Loop (Every 30s)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬────┘
    │       │       │       │       │       │       │       │
    ▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼
┌────────┐┌────────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│Config  ││Window  ││Idle  ││Strat ││Dedupe││Priv  ││Mark  ││Logs  │
│Manager ││Detector││Detect││Factory││licator││Filter││down  ││Output│
└────────┘└────────┘└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘
             │                  │
             │                  ▼
             │         ┌──────────────────┐
             │         │    Strategies    │
             │         ├──────────────────┤
             │         │ • Browser        │
             │         │ • Developer      │
             │         │ • Generic        │
             │         └──────────────────┘
             ▼
    ┌─────────────────┐
    │   Windows API   │
    │   (pywin32)     │
    └─────────────────┘
```

## Component Responsibilities

### 1. CLI Interface (`main.py`)
**Responsibilities**:
- Parse command-line arguments
- Setup logging
- Initialize ActivityLogger
- Handle Ctrl+C gracefully

**Dependencies**: None (entry point)

### 2. Activity Logger (`activity_logger.py`)
**Responsibilities**:
- Coordinate all components
- Run polling loop
- Orchestrate data flow
- Handle errors and exceptions

**Dependencies**: All other components

### 3. Config Manager (`config_manager.py`)
**Responsibilities**:
- Load configuration from JSON
- Provide defaults
- Validate settings
- Expose configuration properties

**Dependencies**: None

### 4. Window Detector (`window_detector.py`)
**Responsibilities**:
- Detect foreground window (Win32 API)
- Scan background windows
- Filter by meeting whitelist
- Apply blacklist

**Dependencies**: 
- pywin32 (Win32 API)
- psutil (process info)
- ConfigManager

### 5. Strategy Factory (`strategies/factory.py`)
**Responsibilities**:
- Select appropriate strategy
- Maintain strategy instances
- Priority-based selection

**Dependencies**: All strategy implementations

### 6. Strategy Implementations

#### Browser Strategy (`strategies/browser.py`)
**Responsibilities**:
- Extract URL via UI Automation
- Timeout protection
- Fallback to title
- Handle multiple browsers

**Dependencies**: uiautomation

#### Developer Strategy (`strategies/developer.py`)
**Responsibilities**:
- Parse window titles
- Extract filenames
- Format code references

**Dependencies**: None (title parsing only)

#### Generic Strategy (`strategies/generic.py`)
**Responsibilities**:
- Handle all other apps
- Friendly name mapping
- Basic title extraction

**Dependencies**: None

### 7. Idle Detector (`idle_detector.py`)
**Responsibilities**:
- Monitor keyboard/mouse
- Track last activity time
- Determine idle state
- Run background listeners

**Dependencies**: pynput

### 8. Deduplicator (`deduplicator.py`)
**Responsibilities**:
- Track last logged state
- Compare current vs last
- Decide if should log
- Handle state transitions

**Dependencies**: None

### 9. Privacy Filter (`privacy_filter.py`)
**Responsibilities**:
- Check for sensitive keywords
- Check URL patterns
- Redact sensitive info
- Apply blacklist rules

**Dependencies**: ConfigManager

### 10. Markdown Writer (`markdown_writer.py`)
**Responsibilities**:
- Create daily log files
- Format Markdown tables
- Handle file I/O
- Manage log rotation

**Dependencies**: ConfigManager

## Data Flow

### Polling Cycle (Every 30 seconds)

```
START
  │
  ▼
┌───────────────┐
│ Check Idle?   │
└───┬───────┬───┘
    │ Yes   │ No
    ▼       ▼
 [Log      ┌──────────────────┐
  IDLE]    │ Get Foreground   │
    │      │ Window           │
    │      └────────┬─────────┘
    │               ▼
    │      ┌──────────────────┐
    │      │ Select Strategy  │
    │      └────────┬─────────┘
    │               ▼
    │      ┌──────────────────┐
    │      │ Extract Activity │
    │      │ (URL/Title)      │
    │      └────────┬─────────┘
    │               ▼
    │      ┌──────────────────┐
    │      │ Scan Background  │
    │      │ (Meetings)       │
    │      └────────┬─────────┘
    │               ▼
    │      ┌──────────────────┐
    │      │ Apply Privacy    │
    │      │ Filter           │
    │      └────────┬─────────┘
    │               ▼
    │      ┌──────────────────┐
    │      │ Check Duplicate? │
    │      └───┬──────────┬───┘
    │          │ Yes      │ No
    │          ▼          ▼
    │       [Skip]   ┌──────────┐
    │          │     │ Write to │
    │          │     │ Markdown │
    │          │     └─────┬────┘
    └──────────┴───────────┘
                   │
                   ▼
              ┌─────────┐
              │ Sleep   │
              │ 30s     │
              └─────────┘
                   │
                   └──► REPEAT
```

## Strategy Selection Flow

```
Process Name
     │
     ▼
┌─────────────────┐
│ Is Browser?     │─── Yes ──► BrowserStrategy
│ (chrome.exe,    │              │
│  msedge.exe)    │              ▼
└────────┬────────┘        ┌──────────────┐
         │ No              │ UI Automation│
         ▼                 │ Extract URL  │
┌─────────────────┐        └──────────────┘
│ Is Dev Tool?    │─── Yes ──► DeveloperToolsStrategy
│ (Code.exe,      │              │
│  powershell.exe)│              ▼
└────────┬────────┘        ┌──────────────┐
         │ No              │ Parse Title  │
         ▼                 │ Extract File │
┌─────────────────┐        └──────────────┘
│ Generic         │
│ (Everything     │
│  else)          │
└────────┬────────┘
         │
         ▼
   ┌──────────────┐
   │ Process Name │
   │ + Title      │
   └──────────────┘
```

## Thread Model

```
Main Thread
    │
    ├─► Polling Loop (blocking, sleeps)
    │
    └─► Event Handlers (synchronous)

Background Threads (pynput)
    │
    ├─► Mouse Listener (updates timestamp)
    │
    └─► Keyboard Listener (updates timestamp)
```

**Note**: All components run on main thread except idle detection listeners.

## Error Handling Strategy

```
Level 1: Component-Level
    │
    ├─► Try-Except in each method
    │   └─► Log error, return None/safe default
    │
Level 2: Integration-Level
    │
    ├─► Polling loop catches exceptions
    │   └─► Log error, continue polling
    │
Level 3: Application-Level
    │
    └─► Main catches KeyboardInterrupt & errors
        └─► Graceful shutdown
```

## File System Layout

```
Project Root
│
├── config/
│   └── config.json          [Configuration]
│
├── src/
│   ├── *.py                 [Application Code]
│   └── strategies/
│       └── *.py             [Strategy Implementations]
│
├── logs/                    [Output - Auto-created]
│   ├── 2026-01-28_log.md
│   ├── 2026-01-29_log.md
│   └── ...
│
└── tests/                   [Test Suite]
    └── *.py
```

## Dependency Graph

```
main.py
  └── activity_logger.py
       ├── config_manager.py
       │
       ├── window_detector.py
       │    ├── config_manager.py
       │    ├── win32gui (pywin32)
       │    └── psutil
       │
       ├── strategies/factory.py
       │    ├── browser.py
       │    │    ├── config_manager.py
       │    │    └── uiautomation
       │    ├── developer.py
       │    │    └── config_manager.py
       │    └── generic.py
       │
       ├── idle_detector.py
       │    ├── config_manager.py
       │    └── pynput
       │
       ├── deduplicator.py
       │
       ├── privacy_filter.py
       │    └── config_manager.py
       │
       └── markdown_writer.py
            └── config_manager.py
```

## External Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| pywin32 | Windows API access | ≥305 |
| uiautomation | UI element inspection | ≥2.0.18 |
| psutil | Process enumeration | ≥5.9.0 |
| pynput | Input monitoring | ≥1.7.6 |
| pyyaml | YAML support (optional) | ≥6.0 |

## Performance Characteristics

### Time Complexity
- **Window Detection**: O(1) - Win32 API call
- **Background Scan**: O(n) - n = number of windows
- **Strategy Execution**: 
  - Browser: O(1) with timeout
  - Developer: O(1)
  - Generic: O(1)
- **Deduplication**: O(1) - simple comparison
- **Privacy Filter**: O(k) - k = number of keywords

### Space Complexity
- **Memory**: O(1) - constant memory per poll
- **Disk**: O(n) - n = activity changes per day (~1-5MB/day)

### Timing
- **Poll Interval**: 30s (configurable)
- **UI Automation Timeout**: 0.5s
- **Idle Check**: <1ms
- **Write to Disk**: <10ms

## Security Considerations

1. **Privacy**:
   - Keyword filtering
   - URL redaction
   - Local storage only
   - No network calls

2. **Permissions**:
   - User-level access (no admin required)
   - Read window information
   - Monitor input events
   - File system write access

3. **Data Protection**:
   - Logs stored locally
   - Configurable output directory
   - No cloud sync
   - User controls all data

## Scalability

### Current Design
- **Single User**: ✅ Optimized
- **Single Machine**: ✅ Optimized
- **24/7 Operation**: ✅ Tested
- **Multiple Users**: ❌ Not supported
- **Distributed**: ❌ Not supported

### Limitations
- Windows-only (Win32 API dependency)
- Single instance per user
- No database (file-based)
- No real-time sync

## Extension Points

### Easy to Extend
1. **New Strategy**: Implement `ActivityStrategy` interface
2. **New Filter**: Add to `PrivacyFilter`
3. **New Output Format**: Implement writer interface
4. **New Configuration**: Add to `config.json`

### Harder to Extend
1. **Cross-Platform**: Would need OS abstraction layer
2. **Real-Time Sync**: Would need backend service
3. **Multi-User**: Would need database
4. **Plugin System**: Would need dynamic loading

---

**Architecture Status**: ✅ Implemented and Functional
**Last Updated**: 2026-01-28
