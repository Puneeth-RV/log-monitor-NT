# risk_engine.py

import store
import pandas as pd

def get_risk_scores():
    """Calculate a risk score (0–100) for each service based on log patterns."""

    if store.DF.empty:
        return []

    df = store.DF.copy()
    services = df["service"].unique()
    scores = []

    total_logs = len(df)

    for service in services:
        svc_df = df[df["service"] == service]
        svc_count = len(svc_df)

        # ── Factor 1: Error ratio (0–40 points)
        error_count = len(svc_df[svc_df["level"] == "ERROR"])
        error_ratio = error_count / svc_count if svc_count > 0 else 0
        error_score = min(error_ratio * 160, 40)  # 25% errors = max 40 pts

        # ── Factor 2: Warning ratio (0–20 points)
        warn_count = len(svc_df[svc_df["level"] == "WARN"])
        warn_ratio = warn_count / svc_count if svc_count > 0 else 0
        warn_score = min(warn_ratio * 80, 20)  # 25% warnings = max 20 pts

        # ── Factor 3: "failed" keyword frequency (0–25 points)
        failed_count = len(svc_df[svc_df["message"].str.contains("failed", case=False, na=False)])
        failed_ratio = failed_count / svc_count if svc_count > 0 else 0
        failed_score = min(failed_ratio * 100, 25)  # 25% failed = max 25 pts

        # ── Factor 4: Volume share — busier services carry more risk (0–15 points)
        volume_ratio = svc_count / total_logs if total_logs > 0 else 0
        volume_score = min(volume_ratio * 30, 15)  # 50% of all logs = max 15 pts

        # ── Total risk score
        risk = round(error_score + warn_score + failed_score + volume_score)
        risk = min(risk, 100)

        # ── Risk level label
        if risk >= 70:
            level = "CRITICAL"
        elif risk >= 40:
            level = "MODERATE"
        else:
            level = "LOW"

        scores.append({
            "service": service,
            "risk_score": risk,
            "risk_level": level,
            "total_logs": svc_count,
            "errors": error_count,
            "warnings": warn_count,
            "failed_keywords": failed_count,
        })

    # Sort by risk score descending
    scores.sort(key=lambda x: x["risk_score"], reverse=True)

    return scores


if __name__ == "__main__":
    results = get_risk_scores()
    print("=== Risk Scores ===")
    for r in results:
        print(f"{r['service']}: {r['risk_score']} ({r['risk_level']})")