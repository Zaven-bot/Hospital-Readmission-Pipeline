import pandas as pd
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import argparse
import joblib # to save Python objects (like test data)

# === DVC data version tracking ===
def get_dvc_file_hash(path):
    try: 
        with open(path, "r") as f:
            for line in f:
                if "md5:" in line:
                    return line.strip().split(":")[1].strip()
        return "unknown"
    except Exception:
        return "unknown file path was passed into get_dvc_file_hash"

if __name__ == "__main__":
    # === Argument Parsing ===
    parser = argparse.ArgumentParser(description="Train hospital readmission model.")
    parser.add_argument('--input', type=str, required=True) # prepared feature dataset
    parser.add_argument('--run-group', type=str, default=None, help="Group tag for run versioning") # version grouping
    args = parser.parse_args()


    # === Load featured data ===
    df = pd.read_csv(args.input)
    X = df.drop(columns=["readmitted_binary"])
    y = df["readmitted_binary"]

    # === Train/test split ===
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # === Save test set for future evaluations ===
    joblib.dump((X_test, y_test), "data/processed/test_data.pkl")

    # === MLflow experiment logging ===
    # For the next run, use this experiment, and end any run
    # that's currently happening
    mlflow.set_experiment("ReadmissionPipeline")
    mlflow.end_run()

    # Start an MLflow run (log book for this run)
    with mlflow.start_run():
        if args.run_group:
            mlflow.set_tag("run_group", args.run_group)

        # === Log dataset versions (both featured + cleaned) ===
        mlflow.log_param("data_version_featured", get_dvc_file_hash("data/processed/featured_data.csv.dvc"))
        mlflow.log_param("data_version_cleaned", get_dvc_file_hash("data/processed/cleaned_data.csv.dvc"))

        # Log test data artifact
        mlflow.log_artifact("data/processed/test_data.pkl", artifact_path="datasets")

        # === Model hyperparameters ===
        max_depth = 8
        n_estimators = 100
        model_type = "RandomForest"

        # === Log hyperparameters ===
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("n_estimators", n_estimators)

        # === Train the model ===
        model = RandomForestClassifier(max_depth=max_depth, n_estimators=n_estimators, random_state=42)
        model.fit(X_train, y_train)

        # === Predict and Evaluate ===
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, output_dict=True)

        # === Log accuracy + classification report metrics ===
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("precision_1", report["1"]["precision"])
        mlflow.log_metric("recall_1", report["1"]["recall"])
        mlflow.log_metric("f1_score_1", report["1"]["f1-score"])

        # === Save model ===
        mlflow.sklearn.log_model(model, "random_forest_model")
        
        # === Register the model under "ReadmissionModel" ===
        result = mlflow.register_model(
            model_uri=f"runs:/{mlflow.active_run().info.run_id}/random_forest_model",
            name="ReadmissionModel"
        )

        # Transition the model to 'Staging'
        # Assigns the current version a number
        client = MlflowClient()
        client.transition_model_version_stage(
            name="ReadmissionModel",
            version=result.version,
            stage="Staging"
        )

        print(f"✅ Model trained and logged to MLflow — Accuracy: {acc:.4f}")
        
        with open("last_run_id.txt", "w") as f:
            f.write(mlflow.active_run().info.run_id)