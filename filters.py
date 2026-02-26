import pandas as pd
from store import DF  # Live DataFrame built by Person 1's store.py


def filter_logs(
    level: str = None,
    service: str = None,
    from_time: str = None,
    to_time: str = None,
    keyword: str = None,
) -> list[dict]:
    """
    Filter the global DF and return matching rows as a list of dicts.

    Parameters
    ----------
    level     : exact match on the 'level' column  (e.g. "ERROR")
    service   : exact match on the 'service' column (e.g. "MeshDataService")
    from_time : ISO-format string — keep rows where timestamp >= this value
    to_time   : ISO-format string — keep rows where timestamp <= this value
    keyword   : case-insensitive substring match on the 'message' column
    """

    # Start with the full DataFrame; we'll narrow it down filter by filter
    result = DF.copy()

    # ── 1. Filter by log level ────────────────────────────────────────────────
    if level is not None:
        result = result[result["level"] == level]

    # ── 2. Filter by service name ─────────────────────────────────────────────
    if service is not None:
        result = result[result["service"] == service]

    # ── 3. Filter by start time (inclusive) ───────────────────────────────────
    if from_time is not None:
        # Parse the string to a datetime so Pandas can compare it correctly
        result = result[result["timestamp"] >= pd.to_datetime(from_time)]

    # ── 4. Filter by end time (inclusive) ─────────────────────────────────────
    if to_time is not None:
        result = result[result["timestamp"] <= pd.to_datetime(to_time)]

    # ── 5. Filter by keyword in message (case-insensitive) ────────────────────
    if keyword is not None:
        result = result[result["message"].str.contains(keyword, case=False, na=False)]

    # ── Convert timestamp to string so the result is JSON-serialisable ────────
    result = result.copy()
    result["timestamp"] = result["timestamp"].astype(str)

    # Return as a plain list of dicts
    return result.to_dict(orient="records")


# ── Quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":

    # 1. Filter by level
    rows = filter_logs(level="ERROR")
    print(f"level=ERROR        → {len(rows)} row(s): {rows}")

    # 2. Filter by service
    rows = filter_logs(service="MeshDataService")
    print(f"service=MeshDataService → {len(rows)} row(s)")

    # 3. Filter by from_time
    rows = filter_logs(from_time="2026-02-19 19:06:36")
    print(f"from_time=19:06:36  → {len(rows)} row(s)")

    # 4. Filter by to_time
    rows = filter_logs(to_time="2026-02-19 19:06:36")
    print(f"to_time=19:06:36    → {len(rows)} row(s)")

    # 5. Filter by keyword
    rows = filter_logs(keyword="timeout")
    print(f"keyword=timeout     → {len(rows)} row(s): {rows}")

    # 6. Combined filter (bonus)
    rows = filter_logs(service="MeshDataService", level="ERROR")
    print(f"service+level combo → {len(rows)} row(s)")
