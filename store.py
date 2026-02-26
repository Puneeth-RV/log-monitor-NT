import re
import pandas as pd

# Path to the log file
LOG_FILE = "sample-application.log"

# Regex pattern to match each log line
# Example: 2026-02-19 19:06:35.430  WARN 10000 --- [nio-8080-exec-17] c.n.p.service.MeshDataService      : Failed to ...
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)"  # timestamp
    r"\s+(?P<level>WARN|ERROR|INFO|DEBUG)"                          # log level
    r"\s+(?P<thread_id>\d+)"                                        # thread id (numeric)
    r"\s+---\s+\[(?P<thread>[^\]]+)\]"                             # thread name in brackets
    r"\s+[\w.]+\.(?P<service>\w+)"                                  # service: last segment after final dot
    r"\s*:\s+(?P<message>.+)$"                                      # message after colon
)

# Global DataFrame importable by other modules
DF = pd.DataFrame()


def reload_logs():
    """Re-reads the log file and rebuilds the global DF."""
    global DF

    rows = []

    # Read the log file line by line
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            # Attempt to match the line against the pattern
            match = LOG_PATTERN.match(line)
            if not match:
                # Skip lines that don't match the expected format
                continue

            # Extract named groups from the regex match
            rows.append(match.groupdict())

    # Build DataFrame from matched rows
    DF = pd.DataFrame(rows, columns=["timestamp", "level", "thread_id", "thread", "service", "message"])

    # Cast timestamp to datetime64
    DF["timestamp"] = pd.to_datetime(DF["timestamp"])

    # Ensure string columns are typed as str (object)
    for col in ["level", "thread_id", "thread", "service", "message"]:
        DF[col] = DF[col].astype(str)


# Load logs on module import so DF is ready when other modules import it
reload_logs()


if __name__ == "__main__":
    print("=== DF.head() ===")
    print(DF.head())
    print("\n=== DF.dtypes ===")
    print(DF.dtypes)
    print(f"\nTotal rows: {len(DF)}")

