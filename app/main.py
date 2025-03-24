from fastapi import FastAPI, Response
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
import pandas as pd

app = FastAPI()

REQUEST_COUNT = Counter("request_count", "Total number of requests")

DRIFTED_FEATURES_SHARE = Gauge("drifted_features_share", "Share of drifted features detected by Evidently")

data_drift_report = Report(metrics=[DataDriftPreset()])

# Create a reference dataset as a DataFrame
reference_data = pd.DataFrame([
    {"feature1": 1.0, "feature2": 2.0},
    {"feature1": 1.2, "feature2": 2.1},
    {"feature1": 1.4, "feature2": 2.2},
])

@app.get("/")
def home():
    REQUEST_COUNT.inc()
    
    # Convert your current data into a DataFrame
    current_data = pd.DataFrame([
        {"feature1": 1.0, "feature2": 2.0},
        {"feature1": 1.1, "feature2": 2.2},
    ])

    # Run Evidently with DataFrames
    data_drift_report.run(current_data=current_data, reference_data=reference_data)
    
    # Extract drift metrics from Evidently's output
    drift_results = data_drift_report.as_dict()
    try:
        drift_share = drift_results["metrics"][0]["result"]["drift_share"]
        DRIFTED_FEATURES_SHARE.set(drift_share)
    except (KeyError, IndexError):
        DRIFTED_FEATURES_SHARE.set(0.0)

    return {"message": "Hello, World"}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
