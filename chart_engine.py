# chart_engine.py

import store
import pandas as pd

def get_chart_data(level=None, service=None, from_time=None, to_time=None, keyword=None):
    """Return per-minute ERROR log counts as a list of time/count dicts.
       Accepts optional filters to match the current filter state."""

    df = store.DF.copy()

    if df.empty:
        return []

    # Apply filters if provided
    if level is not None:
        df = df[df["level"] == level]
    else:
        # Default: show only ERROR level
        df = df[df["level"] == "ERROR"]

    if service is not None:
        df = df[df["service"] == service]

    if from_time is not None:
        df = df[df["timestamp"] >= pd.to_datetime(from_time)]

    if to_time is not None:
        df = df[df["timestamp"] <= pd.to_datetime(to_time)]

    if keyword is not None:
        df = df[df["message"].str.contains(keyword, case=False, na=False)]

    if df.empty:
        return []

    # Set timestamp as the index so we can use resample
    df = df.set_index("timestamp")

    # Resample by 1-minute buckets
    resampled = df.resample("1min").size()

    # Drop empty buckets
    resampled = resampled[resampled > 0]

    # Convert to list of dicts
    chart_data = [
        {"time": ts.strftime("%H:%M"), "count": int(count)}
        for ts, count in resampled.items()
    ]

    return chart_data


if __name__ == "__main__":
    data = get_chart_data()
    print("=== Chart Data ===")
    if not data:
        print("No ERROR data to chart.")
    for point in data:
        print(point)