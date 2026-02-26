import pandas as pd
import store  # Use store.DF so we always get the latest DataFrame


def filter_logs(
    level: str = None,
    service: str = None,
    from_time: str = None,
    to_time: str = None,
    keyword: str = None,
) -> list[dict]:
    """
    Filter the global DF and return matching rows as a list of dicts.
    """

    # Start with the full DataFrame — always get the latest from store
    result = store.DF.copy()

    # ── 1. Filter by log level
    if level is not None:
        result = result[result["level"] == level]

    # ── 2. Filter by service name
    if service is not None:
        result = result[result["service"] == service]

    # ── 3. Filter by start time (inclusive)
    if from_time is not None:
        result = result[result["timestamp"] >= pd.to_datetime(from_time)]

    # ── 4. Filter by end time (inclusive)
    if to_time is not None:
        result = result[result["timestamp"] <= pd.to_datetime(to_time)]

    # ── 5. Filter by keyword in message (case-insensitive)
    if keyword is not None:
        result = result[result["message"].str.contains(keyword, case=False, na=False)]

    # ── Convert timestamp to string so the result is JSON-serialisable
    result = result.copy()
    result["timestamp"] = result["timestamp"].astype(str)

    # Return as a plain list of dicts
    return result.to_dict(orient="records")


# ── Quick smoke-test
if __name__ == "__main__":
    rows = filter_logs(level="ERROR")
    print(f"level=ERROR        → {len(rows)} row(s)")

    rows = filter_logs(service="MeshDataService")
    print(f"service=MeshDataService → {len(rows)} row(s)")

    rows = filter_logs(keyword="timeout")
    print(f"keyword=timeout     → {len(rows)} row(s)")