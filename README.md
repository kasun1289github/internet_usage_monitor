# Website-by-Website Traffic Monitor — Setup Guide

Tracks how much data each website (YouTube, Facebook, Gmail, ChatGPT, Claude,
etc.) uses in your browser, including sites protected by Encrypted Client
Hello (ECH), like YouTube.

## How it works (short version)

Your browser is pointed at a local proxy (`mitmproxy`) instead of the
internet directly. The proxy decrypts traffic on the fly, reads the real
site each request goes to, and logs bytes per site — live in a terminal
window and to a CSV file.

## Files you need

- `traffic_addon.py` — the tracking logic + the list of known sites
- `start_traffic_monitor.bat` — one-click launcher for windows

Keep both files together in the same folder, e.g.:
```
C:\Users\<you>\Desktop\internet_usage_monitor
```

## One-time setup on a new machine

1. **Install Python 3** (if not already installed): https://www.python.org/downloads/
   During install, tick **"Add Python to PATH"**.

2. **Install mitmproxy and pywin32** — open Command Prompt and run:
   ```
   pip install mitmproxy
   pip install pywin32
   ```
   
3. **Create the folder** for this tool, e.g. `C:\Users\<you>\Desktop\internet_usage_monitor`,
   and put `traffic_addon.py` and `start_traffic_monitor.bat` inside it.

4. **Find your Chrome install path.** The `.bat` file assumes:
   ```
   C:\Program Files\Google\Chrome\Application\chrome.exe
   ```
   If Chrome is installed somewhere else on this machine, open
   `start_traffic_monitor.bat` in Notepad and update that path (appears
   twice, once per launch branch).

5. **New Day Data Handling**
   - The application automatically detects when a new day starts.
   - A Windows popup notification appears to inform the user that a new day has started. You need to click Ok button inorder to proceed.
   - The previous day's traffic data is saved before the counters are reset.
   - A new CSV file is then created for the new day.
   - Daily traffic counters are reset to ensure accurate usage tracking for each day.

## Running it (every time)

1. Double-click `start_traffic_monitor.bat` — **do not** run it "as
   Administrator" (that can cause file-permission errors later).
   - If nothing is running yet, it starts cleanly.
   - If a monitor is already running, it asks whether to kill it and
     start fresh, or start a second instance on another port.
2. It will:
   - Close any open Chrome windows (needed so the proxy setting applies)
   - Start the "Traffic Monitor" window — this is where you watch live
     stats, updated every 10 seconds
   - Launch Chrome through the proxy and open `http://mitm.it`
3. **First time only on this machine:** on the `mitm.it` page, download
   and install the certificate for Windows:
   - Double-click the downloaded `.cer` file
   - **Install Certificate** → **Local Machine** → **Place all certificates in the following store** → **Trusted Root Certification Authorities**
   - Confirm the admin prompt
   - Without this step, every HTTPS site will show a security warning
4. Browse normally. Watch the **Traffic Monitor** window for live
   numbers by site. A CSV file (e.g. `usage_20260926_181530.csv`) is
   created in the same folder, timestamped to the moment you started
   that session — every run gets its own file, nothing gets overwritten.

## Customizing which sites get grouped

Near the top of `traffic_addon.py` is a dictionary:
```python
DOMAIN_GROUPS = {
    "YouTube": ["youtube.com", "ytimg.com", "googlevideo.com", ...],
    "Facebook": ["facebook.com", "fbcdn.net", "fbsbx.com"],
    "Gmail": ["mail.google.com", "gmail.com"],
    "ChatGPT": ["chatgpt.com", "openai.com", ...],
    "Claude": ["claude.ai", "anthropic.com"],
    ...
}
```
This is **not a filter** — every site is tracked automatically whether or not it's listed here. This dictionary only controls the display name:
sites in the list get combined into one friendly line (e.g. all of YouTube's various server domains show up as one "YouTube" total); sites
not listed just show up under their own raw hostname instead. Add more entries any time — just restart the `.bat` file afterward.

## Traffic Data & Daily Handling

 - Traffic usage is recorded in a CSV file at regular intervals.
 - Each record includes the timestamp, website, traffic generated during the interval, and  cumulative traffic usage.
 - The bytes field represents the traffic generated since the previous report.
 - The accumulative_bytes field represents the total traffic consumed by that website during the current day.
 - Human-readable values are also provided in KB, MB, GB, etc.
 - When a new day is detected, a Windows popup notification appears.
 - The previous day's traffic data is saved, counters are reset, and a new CSV file is created for the new day.


## Troubleshooting

- **"Address already in use" / port error** — an old `mitmdump` process
  is still running from a previous session. Re-run the `.bat` file; it detects this and offers to kill the old one.

- **`PermissionError` writing the CSV** — the file is open in Excel/
  Notepad, or was created by a previous *admin-mode* run. Close any program with it open, delete the old CSV, and make sure you're not
  running the `.bat` "as Administrator".

- **A site shows almost no traffic even though you used it a lot** —
  check whether Chrome was actually launched *through this session's* proxy window (an already-open Chrome window won't pick up the proxy
  setting; the `.bat` file closes existing Chrome windows first for this reason).

- **Certificate warnings on every site** — the mitmproxy certificate
  either wasn't installed, or was installed to the wrong certificate store. Redo the `http://mitm.it` step above, making sure to choose
  **Local Machine** and **Trusted Root Certification Authorities**.
