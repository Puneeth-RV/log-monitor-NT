# alert_engine.py

import store
import pandas as pd
from datetime import datetime, timedelta

def _format_breakdown(breakdown):
    """Format service breakdown as a readable string."""
    parts = [f"{svc} ({count})" for svc, count in breakdown.items()]
    return ", ".join(parts)

def run_alerts():
    """Run all alert rules against the last 10 minutes of log data."""

    if store.DF.empty:
        return []

    now = store.DF["timestamp"].max()
    window_start = now - timedelta(minutes=10)
    time_label = f"{window_start.strftime('%H:%M:%S')} – {now.strftime('%H:%M:%S')}"

    recent = store.DF[store.DF["timestamp"] >= window_start]

    alerts = []

    # --- Rule 1: ERROR count threshold ---
    error_rows = recent[recent["level"] == "ERROR"]
    error_count = len(error_rows)

    if error_count > 5:
        severity = "HIGH" if error_count > 10 else "LOW"
        service_breakdown = error_rows["service"].value_counts().to_dict()

        reason = (
            f"Detected {error_count} ERROR-level logs within a 10-minute window "
            f"({time_label}). "
            f"Affected services: {_format_breakdown(service_breakdown)}."
        )

        alerts.append({
            "name": "Error Rate Threshold Exceeded",
            "severity": severity,
            "reason": reason,
            "count": error_count,
            "window": "10 min",
            "service_breakdown": service_breakdown,
        })

    # --- Rule 2: Keyword "failed" frequency ---
    failed_rows = recent[recent["message"].str.contains("failed", case=False, na=False)]
    failed_count = len(failed_rows)

    if failed_count > 3:
        service_breakdown = failed_rows["service"].value_counts().to_dict()

        reason = (
            f"The keyword \"failed\" appeared {failed_count} times in log messages "
            f"over the last 10 minutes ({time_label}). "
            f"Affected services: {_format_breakdown(service_breakdown)}."
        )

        alerts.append({
            "name": "Failure Keyword Spike",
            "severity": "LOW",
            "reason": reason,
            "count": failed_count,
            "window": "10 min",
            "service_breakdown": service_breakdown,
        })

    # --- Rule 3: Cascading Failure Detection ---
    services = recent["service"].unique()

    for service in services:
        svc_df = recent[recent["service"] == service].sort_values("timestamp")

        if len(svc_df) < 5:
            continue

        svc_df = svc_df.set_index("timestamp")
        buckets = svc_df.resample("2min")

        prev_error_spike = False
        prev_error_count = 0
        prev_bucket_label = ""

        for bucket_time, bucket_df in buckets:
            bucket_errors = len(bucket_df[bucket_df["level"] == "ERROR"])
            bucket_warns = len(bucket_df[bucket_df["level"] == "WARN"])

            if prev_error_spike and bucket_warns >= 3:
                reason = (
                    f"Potential cascading failure detected in {service}. "
                    f"An ERROR spike of {prev_error_count} at {prev_bucket_label} was immediately "
                    f"followed by a WARN spike of {bucket_warns} at {bucket_time.strftime('%H:%M')}. "
                    f"This pattern suggests upstream errors may be triggering downstream warnings."
                )

                alerts.append({
                    "name": f"Cascading Failure — {service}",
                    "severity": "CRITICAL",
                    "reason": reason,
                    "count": prev_error_count + bucket_warns,
                    "window": "2 min",
                    "service_breakdown": {service: prev_error_count + bucket_warns},
                })
                break

            prev_error_spike = bucket_errors >= 3
            prev_error_count = bucket_errors
            prev_bucket_label = bucket_time.strftime('%H:%M')

    return alerts


if __name__ == "__main__":
    results = run_alerts()
    print("=== Alerts ===")
    if not results:
        print("No alerts fired.")
    for alert in results:
        print(alert)