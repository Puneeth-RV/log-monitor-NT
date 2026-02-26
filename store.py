import re
import pandas as pd

# Path to the log file
LOG_FILE = "sample-application.log"

# Regex pattern to match each log line
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)"
    r"\s+(?P<level>WARN|ERROR|INFO|DEBUG)"
    r"\s+(?P<thread_id>\d+)"
    r"\s+---\s+\[(?P<thread>[^\]]+)\]"
    r"\s+[\w.]+\.(?P<service>\w+)"
    r"\s*:\s+(?P<message>.+)$"
)

# Global DataFrame importable by other modules
DF = pd.DataFrame()

# ── Real-time simulation state ──────────────────────────
_all_rows = []        # All parsed rows from the log file
_current_index = 0    # How many rows are currently loaded into DF
BATCH_SIZE = 200      # Load 200 rows every reload call (~2000 logs in 20 seconds)


def _parse_all_logs():
    """Parse the entire log file once and store rows in memory."""
    global _all_rows

    if _all_rows:
        return  # Already parsed

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            match = LOG_PATTERN.match(line)
            if not match:
                continue
            _all_rows.append(match.groupdict())


def reload_logs():
    """Each call loads the next batch of logs, simulating real-time ingestion."""
    global DF, _current_index

    # Parse all lines on first call
    _parse_all_logs()

    # Load next batch
    _current_index = min(_current_index + BATCH_SIZE, len(_all_rows))

    # Build DataFrame from rows loaded so far
    DF = pd.DataFrame(_all_rows[:_current_index],
                       columns=["timestamp", "level", "thread_id", "thread", "service", "message"])

    # Cast timestamp to datetime64
    DF["timestamp"] = pd.to_datetime(DF["timestamp"])

    # Ensure string columns
    for col in ["level", "thread_id", "thread", "service", "message"]:
        DF[col] = DF[col].astype(str)

    print(f"[store] Loaded {_current_index}/{len(_all_rows)} logs")


# Load first batch on import
reload_logs()


if __name__ == "__main__":
    print("=== DF.head() ===")
    print(DF.head())
    print(f"\n=== DF.dtypes ===")
    print(DF.dtypes)
    print(f"\nTotal rows loaded: {len(DF)}")
    print(f"Total rows parsed: {len(_all_rows)}")