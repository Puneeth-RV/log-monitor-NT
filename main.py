# Run with: uvicorn main:app --reload

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import io
import csv

# --- Import project modules ---
import store
from filters import filter_logs
from alert_engine import run_alerts
from chart_engine import get_chart_data

# --- App setup ---
app = FastAPI(title="Log Monitor")

# CORS — allow all origins so the frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (index.html lives here)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Routes ---

# Serve the Web UI at root
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


# GET /logs — filter and return log entries as JSON
@app.get("/logs")
def get_logs(
    level: str = Query(None),
    service: str = Query(None),
    from_time: str = Query(None),
    to_time: str = Query(None),
    keyword: str = Query(None),
):
    results = filter_logs(
        level=level if level and level != "ALL" else None,
        service=service if service and service != "ALL" else None,
        from_time=from_time if from_time else None,
        to_time=to_time if to_time else None,
        keyword=keyword if keyword else None,
    )
    return results


# GET /alerts — run alert rules and return fired alerts
@app.get("/alerts")
def get_alerts():
    return run_alerts()


# GET /chart — error counts grouped by minute for the chart (supports filters)
@app.get("/chart")
def get_chart(
    level: str = Query(None),
    service: str = Query(None),
    from_time: str = Query(None),
    to_time: str = Query(None),
    keyword: str = Query(None),
):
    return get_chart_data(
        level=level if level and level != "ALL" else None,
        service=service if service and service != "ALL" else None,
        from_time=from_time if from_time else None,
        to_time=to_time if to_time else None,
        keyword=keyword if keyword else None,
    )


# GET /export — same filters as /logs but returns a CSV file download
@app.get("/export")
def export_csv(
    level: str = Query(None),
    service: str = Query(None),
    from_time: str = Query(None),
    to_time: str = Query(None),
    keyword: str = Query(None),
):
    results = filter_logs(
        level=level if level and level != "ALL" else None,
        service=service if service and service != "ALL" else None,
        from_time=from_time if from_time else None,
        to_time=to_time if to_time else None,
        keyword=keyword if keyword else None,
    )

    # Write results to an in-memory CSV
    output = io.StringIO()
    if results:
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    else:
        output.write("No matching logs found.\n")

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=filtered_logs.csv"},
    )


# --- Background scheduler: reload logs every 2 seconds for real-time simulation ---
scheduler = BackgroundScheduler()
scheduler.add_job(store.reload_logs, "interval", seconds=2)
scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()