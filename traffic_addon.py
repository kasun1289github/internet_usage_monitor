import csv
import os
import threading
import time
from collections import defaultdict
from mitmproxy import http


# ============================================================
# CONFIGURATION
# ============================================================

# Production mode
TEST_MODE = False

# How often traffic is written to CSV
REPORT_INTERVAL = 10

# Only used when TEST_MODE = True
TEST_NEW_DAY_INTERVAL = 60


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# WEBSITE GROUPS
# ============================================================

DOMAIN_GROUPS = {
    "YouTube": [
        "youtube.com",
        "ytimg.com",
        "googlevideo.com",
        "ggpht.com",
        "youtube-nocookie.com",
    ],

    "Facebook": [
        "facebook.com",
        "fbcdn.net",
        "fbsbx.com",
    ],

    "Gmail": [
        "mail.google.com",
        "gmail.com",
    ],

    "ChatGPT": [
        "chatgpt.com",
        "openai.com",
        "oaistatic.com",
        "oaiusercontent.com",
    ],

    "Claude": [
        "claude.ai",
        "anthropic.com",
    ],

    "LinkedIn": [
        "linkedin.com",
        "licdn.com",
    ],

    "Google": [
        "google.com",
        "gstatic.com",
        "googleapis.com",
        "gvt1.com",
        "gvt2.com",
    ],

    "Twitter/X": [
        "twitter.com",
        "x.com",
        "twimg.com",
    ],

    "Instagram": [
        "instagram.com",
        "cdninstagram.com",
    ],

    "WhatsApp": [
        "whatsapp.com",
        "whatsapp.net",
    ],

    "Netflix": [
        "netflix.com",
        "nflxvideo.net",
        "nflximg.net",
    ],

    "Microsoft/Edge": [
        "microsoft.com",
        "msn.com",
        "live.com",
        "office.com",
        "windows.net",
    ],

    "GitHub": [
        "github.com",
        "githubusercontent.com",
        "githubcopilot.com",
    ],
}


# ============================================================
# CSV
# ============================================================

def create_csv_path():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(
        DATA_DIR,
        f"usage_{timestamp}.csv"
    )


CSV_PATH = create_csv_path()


# ============================================================
# TRAFFIC COUNTERS
# ============================================================

# Total traffic accumulated during the current day
bytes_by_group = defaultdict(int)

# Traffic value written during the previous CSV update.
# Used to calculate incremental/delta traffic.
last_written_bytes = defaultdict(int)


# ============================================================
# DATE / THREAD CONTROL
# ============================================================

start_time = time.time()

current_date = (
    time.strftime("%Y-%m-%d")
)

last_day_check = time.time()

lock = threading.Lock()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def group_for(hostname):
    """
    Return the website group for a hostname.
    """

    if not hostname:
        return "Other"

    hostname = hostname.lower().split(":")[0]

    for group, domains in DOMAIN_GROUPS.items():

        for domain in domains:

            if (
                hostname == domain
                or hostname.endswith("." + domain)
            ):
                return group

    return hostname


def human(n):
    """
    Convert bytes into a human-readable value.
    """

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    value = float(n)

    for unit in units:

        if value < 1024:
            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} PB"


# ============================================================
# CSV WRITING
# ============================================================

def write_csv():
    """
    Write incremental traffic and cumulative traffic.

    bytes:
        Traffic generated since the previous CSV write.

    accumulative_bytes:
        Total traffic for the site since the start of the day.
    """

    global last_written_bytes

    with lock:

        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        file_exists = os.path.exists(CSV_PATH)

        with open(
            CSV_PATH,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            if not file_exists:

                writer.writerow([
                    "timestamp",
                    "site",
                    "bytes",
                    "human_bytes",
                    "accumulative_bytes",
                    "accumulative_human"
                ])

            for site, total_bytes in bytes_by_group.items():

                previous_bytes = (
                    last_written_bytes.get(site, 0)
                )

                # Traffic generated since last report
                delta_bytes = (
                    total_bytes - previous_bytes
                )

                if delta_bytes > 0:

                    writer.writerow([
                        timestamp,
                        site,
                        delta_bytes,
                        human(delta_bytes),

                        # Cumulative value
                        total_bytes,
                        human(total_bytes)
                    ])

                # Remember current cumulative value
                last_written_bytes[site] = total_bytes


# ============================================================
# NEW DAY DIALOG
# ============================================================

def show_new_day_dialog(previous_date, new_date):

    import ctypes

    message = (
        "A new day has started.\n\n"
        f"Previous day: {previous_date}\n"
        f"New day:      {new_date}\n\n"
        "The previous day's Data-Usage file will be saved.\n"
        "A new Data-Usage file will be created for today."
    )

    ctypes.windll.user32.MessageBoxW(
        0,
        message,
        "Traffic Monitor - New Day",
        0 | 64   # OK button + Information icon
    )

# ============================================================
# NEW DAY HANDLING
# ============================================================

def prompt_for_new_day():

    global CSV_PATH
    global bytes_by_group
    global last_written_bytes
    global start_time
    global current_date
    global last_day_check

    previous_date = current_date

    if TEST_MODE:

        new_date = time.strftime(
            "%Y-%m-%d",
            time.localtime(
                time.mktime(
                    time.strptime(
                        current_date,
                        "%Y-%m-%d"
                    )
                ) + 86400
            )
        )

    else:

        new_date = time.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # Show notification
    # --------------------------------------------------------

    show_new_day_dialog(
        previous_date,
        new_date
    )

    # --------------------------------------------------------
    # Save final traffic for previous day
    # --------------------------------------------------------

    write_csv()

    # --------------------------------------------------------
    # Reset counters
    # --------------------------------------------------------

    with lock:

        bytes_by_group.clear()
        last_written_bytes.clear()

        # ----------------------------------------------------
        # Create new CSV
        # ----------------------------------------------------

        CSV_PATH = create_csv_path()

        # ----------------------------------------------------
        # Reset monitoring state
        # ----------------------------------------------------

        start_time = time.time()
        current_date = new_date
        last_day_check = time.time()

    print()
    print("==========================================")
    print("NEW DAY STARTED")
    print("==========================================")
    print(f"Previous day : {previous_date}")
    print(f"New day      : {new_date}")
    print(f"New CSV      : {CSV_PATH}")
    print("Counters     : RESET")
    print("==========================================")
    print()


# ============================================================
# REPORT LOOP
# ============================================================

def report_loop():

    global last_day_check

    while True:

        time.sleep(REPORT_INTERVAL)

        # ----------------------------------------------------
        # Check for new day
        # ----------------------------------------------------

        if TEST_MODE:

            if (
                time.time() - last_day_check
                >= TEST_NEW_DAY_INTERVAL
            ):

                prompt_for_new_day()

        else:

            actual_date = time.strftime(
                "%Y-%m-%d"
            )

            if actual_date != current_date:

                prompt_for_new_day()

        # ----------------------------------------------------
        # Write traffic
        # ----------------------------------------------------

        write_csv()

        # ----------------------------------------------------
        # Console report
        # ----------------------------------------------------

        with lock:

            total_bytes = sum(
                bytes_by_group.values()
            )

            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Total today: {human(total_bytes)}"
            )

            for site, value in sorted(
                bytes_by_group.items()
            ):

                if value > 0:

                    print(
                        f"    {site:<20} "
                        f"{human(value)}"
                    )


# ============================================================
# MITMPROXY TRAFFIC TRACKER
# ============================================================

class TrafficTracker:

    def response(self, flow: http.HTTPFlow):

        try:

            hostname = flow.request.pretty_host

            group = group_for(hostname)

            request_bytes = 0
            response_bytes = 0

            # ------------------------------------------------
            # Request body
            # ------------------------------------------------

            if flow.request.raw_content:

                request_bytes = len(
                    flow.request.raw_content
                )

            # ------------------------------------------------
            # Response body
            # ------------------------------------------------

            if flow.response:

                if flow.response.raw_content:

                    response_bytes = len(
                        flow.response.raw_content
                    )

            total_bytes = (
                request_bytes +
                response_bytes
            )

            if total_bytes > 0:

                with lock:

                    bytes_by_group[group] += (
                        total_bytes
                    )

        except Exception as e:

            print(
                f"Traffic tracking error: {e}"
            )


# ============================================================
# START REPORT THREAD
# ============================================================

threading.Thread(
    target=report_loop,
    daemon=True
).start()


# ============================================================
# STARTUP INFORMATION
# ============================================================

print()
print("==========================================")
print("       WEBSITE TRAFFIC MONITOR")
print("==========================================")
print(f"Mode        : {'TEST' if TEST_MODE else 'PRODUCTION'}")
print(f"Date check  : {'60 second test' if TEST_MODE else 'Calendar day'}")
print(f"Report      : Every {REPORT_INTERVAL} seconds")
print(f"Data folder : {DATA_DIR}")
print(f"CSV file    : {CSV_PATH}")
print("==========================================")
print()


addons = [
    TrafficTracker()
]