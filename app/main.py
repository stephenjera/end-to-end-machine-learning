import os

import mlflow
import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

app = FastAPI()

REQUEST_COUNT = Counter("request_count", "Total number of requests")

DRIFTED_FEATURES_SHARE = Gauge(
    "drifted_features_share", "Share of drifted features detected by Evidently"
)

data_drift_report = Report(metrics=[DataDriftPreset()])

# Create a reference dataset as a DataFrame
reference_data = pd.DataFrame(
    [
        {"feature1": 1.0, "feature2": 2.0},
        {"feature1": 1.2, "feature2": 2.1},
        {"feature1": 1.4, "feature2": 2.2},
    ]
)


@app.get("/")
def home():
    REQUEST_COUNT.inc()

    # Convert your current data into a DataFrame
    current_data = pd.DataFrame(
        [
            {"feature1": 1.0, "feature2": 2.0},
            {"feature1": 1.1, "feature2": 2.2},
        ]
    )

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


@app.post("/log-to-mlflow")
def log_to_mlflow():
    """
    Logs parameters and metrics to MLflow for testing purposes.
    """
    try:
        # Set the MLflow tracking URI from environment variable
        mlflow.set_tracking_uri(
            os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
        )

        # Create the experiment if it doesn't exist
        experiment_name = "fastapi"
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
        else:
            experiment_id = experiment.experiment_id

        with mlflow.start_run(experiment_id=experiment_id) as run:
            # Log parameters and metrics
            mlflow.log_param("learning_rate", 0.1)
            mlflow.log_metric("accuracy", 0.9)
            mlflow.log_metric("loss", 0.1)

        return {"message": "Logged to MLflow successfully!", "run_id": run.info.run_id}

    except Exception as e:
        return {"error": str(e)}

