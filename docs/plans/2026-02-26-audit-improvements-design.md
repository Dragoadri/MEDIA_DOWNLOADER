# Media Downloader - Audit & Improvements Design

## Overview

Full audit and improvement of Media Downloader v2.0.0 covering architecture, security, UI/UX, and backend.

## 1. Architecture Refactor

Split `ui/main_window.py` (1430 lines) into focused widgets:

```
ui/
├── main_window.py          # Orchestration only (~200 lines)
├── widgets/
│   ├── source_widget.py    # Platform selector + URL input + auto-detection
│   ├── options_widget.py   # Format + quality + transcription options
│   ├── local_tab.py        # Local download folder tab
│   ├── ssh_tab.py          # SSH configuration tab (connection, saved configs, browse)
│   ├── progress_widget.py  # Progress bar + status label + message log
│   └── styles.py           # Centralized QSS styles (eliminate duplication)
├── ssh_browser.py          # Kept as-is, uses centralized styles
```

Each widget communicates via Qt Signals. Styles centralized in `styles.py`.

## 2. Security Fixes

| Issue | Fix |
|-------|-----|
| Plain-text passwords in JSON | Use `keyring` library for secure credential storage |
| `AutoAddPolicy()` accepts any host key | Switch to `WarningPolicy()` + `~/.ssh/known_hosts` |
| sshpass exposes passwords in process list | Remove SCP/sshpass fallback entirely |
| Bare `except:` clauses (47+ instances) | Replace with specific exceptions + logging |
| `StrictHostKeyChecking=no` in SCP | Removed with SCP fallback |

## 3. UI/UX Improvements

- **Cancel button**: `threading.Event` to signal cancellation; button replaces download during active download
- **SSH upload progress**: Use paramiko `sftp.put()` callback for real-time progress
- **Whisper model selector**: Dropdown with model info (size/speed/quality)
- **Real-time validation**: Visual feedback on URL and SSH fields (green/red borders)
- **Enhanced log**: Timestamps, auto-scroll, copy button
- **Polished Matrix theme**: Better spacing, glow effect on download button, consistent icons, version in title bar
- **Keyboard shortcuts**: Ctrl+V paste URL, Ctrl+D download, Esc cancel

## 4. Backend Improvements

- **Formal logging**: `logging` module with file rotation (5MB, 3 backups) at `~/.youtube_downloader/app.log`
- **Temp file cleanup**: Clean orphaned files on app start and on error
- **Simplified file detection**: Use yt-dlp's `info_dict` for downloaded filepath instead of 50-line heuristic
- **QThread migration**: Replace `threading.Thread` with `QThread` for better Qt integration
- **Dependency bounds**: Add `keyring` to requirements, set upper bounds on critical deps
