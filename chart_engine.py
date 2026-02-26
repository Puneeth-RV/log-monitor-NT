# chart_engine.py

from store import DF
import pandas as pd

def get_chart_data():
    """Return per-minute ERROR log counts as a list of time/count dicts."""
    
    # Filter to ERROR level rows only
    error_df = DF[DF["level"] == "ERROR"].copy()
    
    # Return empty list early if there are no ERROR logs
    if error_df.empty:
        return []
    
    # Set timestamp as the index so we can use resample
    error_df = error_df.set_index("timestamp")
    
    # Resample by 1-minute buckets, counting rows in each bucket
    resampled = error_df.resample("1min").size()
    
    # Drop empty buckets (minutes with zero errors) to keep the output clean
    resampled = resampled[resampled > 0]
    
    # Convert to list of dicts with a human-readable time label
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