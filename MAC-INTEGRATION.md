# macOS Integration

Automate `xplat rename` on macOS using a **launchd folder watcher** (automatic, background) and a **Finder Quick Action** (on-demand, right-click).

## Prerequisites

xplat must be installed and available as a command. The recommended approach is [pipx](README.md#installing-with-pipx):

```bash
brew install pipx
pipx ensurepath
pipx install /path/to/xplat
```

Find your xplat binary path (you'll need this below):

```bash
which xplat
# typical output: /Users/yourname/.local/bin/xplat
```

## 1. Folder Watcher (launchd)

Automatically renames files when they land in a watched folder — ideal for screenshots or download directories.

### How it works

macOS launchd monitors a folder via `WatchPaths`. When any file is added, modified, or removed, it runs `xplat rename` on the folder contents. This survives reboots and sleep/wake cycles.

### Create the wrapper script

launchd runs with a minimal environment that doesn't include Homebrew or pipx paths. A wrapper script sets the PATH explicitly.

Save this as `~/.local/bin/xplat-watch.sh`:

```bash
#!/bin/bash
# xplat folder watcher — called by launchd
# Update XPLAT_PATH to match your pipx installation

XPLAT_PATH="$HOME/.local/bin"
export PATH="$XPLAT_PATH:/usr/local/bin:/usr/bin:/bin"

WATCH_DIR="$1"

if [ -z "$WATCH_DIR" ]; then
    echo "Usage: xplat-watch.sh <directory>" >&2
    exit 1
fi

# Log output for debugging
exec >> "$HOME/.local/log/xplat-watch.log" 2>&1
echo "$(date): xplat rename triggered on $WATCH_DIR"

xplat rename "$WATCH_DIR"
```

Make it executable and create the log directory:

```bash
chmod +x ~/.local/bin/xplat-watch.sh
mkdir -p ~/.local/log
```

### Create the launchd plist

Save this as `~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cadentdev.xplat-watch</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>~/.local/bin/xplat-watch.sh</string>
        <!-- Change this to the folder you want to watch -->
        <string>~/Documents/screencap</string>
    </array>

    <key>WatchPaths</key>
    <array>
        <!-- Change this to the folder you want to watch -->
        <string>~/Documents/screencap</string>
    </array>

    <key>RunAtLoad</key>
    <false/>

    <key>StandardOutPath</key>
    <string>~/.local/log/xplat-watch.log</string>

    <key>StandardErrorPath</key>
    <string>~/.local/log/xplat-watch.log</string>
</dict>
</plist>
```

**Important:** Replace `~/Documents/screencap` (both occurrences) with the folder you want to watch. launchd expands `~` in plist values.

### Load and test

```bash
# Create the watched folder if it doesn't exist
mkdir -p ~/Documents/screencap

# Load the agent
launchctl load ~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist

# Test by dropping a file with a problematic name
cp /etc/hosts ~/Documents/screencap/"My Test File (copy).txt"

# Check the log
cat ~/.local/log/xplat-watch.log

# Verify the file was renamed
ls ~/Documents/screencap/
# expected: my-test-file-copy.txt
```

### Management commands

```bash
# Stop the watcher
launchctl unload ~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist

# Restart after editing the plist
launchctl unload ~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist
launchctl load ~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist

# Check if it's running
launchctl list | grep xplat

# View recent logs
tail -20 ~/.local/log/xplat-watch.log
```

### Watching multiple folders

Add additional paths to both `ProgramArguments` and `WatchPaths`. The wrapper script takes one directory argument, so for multiple folders, create separate plist files (e.g., `com.cadentdev.xplat-watch-downloads.plist`).

## 2. Finder Quick Action (Automator)

Adds "Rename with xplat" to the Finder right-click menu. Select files or folders, right-click, and rename on demand.

### Create the Quick Action

1. Open **Automator** (Spotlight: `Cmd+Space`, type "Automator")
2. Click **New Document**
3. Select **Quick Action** as the document type
4. Configure the workflow settings at the top:
   - **Workflow receives current:** `files or folders`
   - **in:** `Finder`
5. From the left panel, drag **Run Shell Script** into the workflow area
6. Configure the shell script action:
   - **Shell:** `/bin/bash`
   - **Pass input:** `as arguments`
7. Replace the script contents with:

```bash
# Rename with xplat — Finder Quick Action
# Update XPLAT_PATH to match your pipx installation

XPLAT_PATH="$HOME/.local/bin"
export PATH="$XPLAT_PATH:/usr/local/bin:/usr/bin:/bin"

for f in "$@"; do
    xplat rename "$f"
done
```

8. Save as **Rename with xplat** (`Cmd+S`)

The workflow is saved to `~/Library/Services/Rename with xplat.workflow`.

### Using the Quick Action

1. In Finder, select one or more files or folders
2. Right-click (or Control-click)
3. Look for **Quick Actions** > **Rename with xplat**
   - On some macOS versions, it appears directly under **Services** > **Rename with xplat**

### Customization

**Restrict to specific file types:** In step 4, change "files or folders" to a specific type (e.g., "image files") to only show the action for those files.

**Add a notification on completion:** After the "Run Shell Script" action, add a "Display Notification" action with a message like "Files renamed with xplat".

## Troubleshooting

### "xplat: command not found"

Both launchd and Automator use a minimal PATH that doesn't include Homebrew or pipx directories. Verify your xplat path:

```bash
which xplat
```

Update `XPLAT_PATH` in the wrapper script or Automator action to match. Common locations:

- pipx: `~/.local/bin/xplat`
- Homebrew Python: `/opt/homebrew/bin/xplat`
- System Python: `/usr/local/bin/xplat`

### Folder watcher not triggering

```bash
# Check if the agent is loaded
launchctl list | grep xplat

# If not listed, reload
launchctl load ~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist

# Check for plist errors
plutil -lint ~/Library/LaunchAgents/com.cadentdev.xplat-watch.plist
```

### Quick Action not appearing in Finder

- Open **System Settings** > **Privacy & Security** > **Extensions** > **Finder** (or **Added Extensions** on older macOS)
- Ensure "Rename with xplat" is checked
- Try restarting Finder: `killall Finder`

### Viewing logs

```bash
# Folder watcher logs
tail -f ~/.local/log/xplat-watch.log

# Automator errors (check Console.app or:)
log show --predicate 'process == "Automator"' --last 5m
```
