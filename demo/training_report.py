import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def generate_evidently_report():
    # Load your reference data (e.g. training data) and current data (e.g. latest batch)
    reference_data = pd.DataFrame([
        {"feature1": 1.0, "feature2": 2.0},
        {"feature1": 1.2, "feature2": 2.1},
        {"feature1": 1.4, "feature2": 2.2},
    ])
    current_data = pd.DataFrame([
        {"feature1": 1.1, "feature2": 2.0},
        {"feature1": 1.3, "feature2": 2.2},
        {"feature1": 1.5, "feature2": 2.4},
    ])

    # Create the Evidently report with the desired preset
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_data, current_data=current_data)
    
    # Save the report to an HTML file
    report.save_html("evidently_report.html")
    print("Evidently report saved as evidently_report.html")

if __name__ == "__main__":
    generate_evidently_report()
