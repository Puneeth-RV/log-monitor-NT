# alert_engine.py

from store import DF
import pandas as pd
from datetime import datetime, timedelta

def run_alerts():
    """Run all alert rules against the last 10 minutes of log data."""
    
    # Get current time and calculate the 10-minute window start
    now = datetime.now()
    window_start = now - timedelta(minutes=10)
    
    # Filter DataFrame to only include rows within the last 10 minutes
    recent = DF[DF["timestamp"] >= window_start]
    
    alerts = []
    
    # --- Rule 1: ERROR count threshold ---
    # Filter for ERROR level logs in the window
    error_rows = recent[recent["level"] == "ERROR"]
    error_count = len(error_rows)
    
    if error_count > 5:
        # Determine severity based on count
        severity = "HIGH" if error_count > 10 else "LOW"
        
        # Build a per-service breakdown of error counts
        service_breakdown = error_rows["service"].value_counts().to_dict()
        
        # Format a human-readable reason string
        reason = (
            f"{error_count} ERROR logs detected in the last 10 minutes "
            f"(window: {window_start.strftime('%H:%M:%S')} - {now.strftime('%H:%M:%S')}). "
            f"Service breakdown: {service_breakdown}."
        )
        
        alerts.append({
            "name": "High ERROR Rate",
            "severity": severity,
            "reason": reason,
            "count": error_count,
            "window": "10 minutes",
            "service_breakdown": service_breakdown,
        })
    
    # --- Rule 2: Keyword "failed" frequency ---
    # Search for the keyword "failed" (case-insensitive) in the message column
    failed_rows = recent[recent["message"].str.contains("failed", case=False, na=False)]
    failed_count = len(failed_rows)
    
    if failed_count > 3:
        # Build a per-service breakdown for failed keyword hits
        service_breakdown = failed_rows["service"].value_counts().to_dict()
        
        reason = (
            f"Keyword 'failed' appeared {failed_count} times in the last 10 minutes "
            f"(window: {window_start.strftime('%H:%M:%S')} - {now.strftime('%H:%M:%S')}). "
            f"Service breakdown: {service_breakdown}."
        )
        
        alerts.append({
            "name": "Keyword 'failed' Spike",
            "severity": "LOW",
            "reason": reason,
            "count": failed_count,
            "window": "10 minutes",
            "service_breakdown": service_breakdown,
        })
    
    # Return all fired alerts (empty list if none triggered)
    return alerts


if __name__ == "__main__":
    results = run_alerts()
    print("=== Alerts ===")
    if not results:
        print("No alerts fired.")
    for alert in results:
        print(alert)