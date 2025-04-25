import mlflow
import mlflow.sklearn
import joblib # to save Python objects (like test data)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from src.feature_engineering import prepare_features # loads / encodes / splits data
from mlflow.tracking import MlflowClient

# === DVC data version tracking ===
def get_dvc_file_hash(path="data/processed/cleaned_data.csv.dvc"):
    with open(path, "r") as f:
        for line in f:
            if "md5:" in line:
                return line.strip().split(":")[1].strip()
    return "unknown"

# === Load features and labels ===
X_train, X_test, y_train, y_test = prepare_features("data/processed/cleaned_data.csv")
joblib.dump((X_test, y_test), 'data/processed/test_data.pkl')

# === MLflow tracking ===
mlflow.end_run()  # end any lingering run

# Start an MLflow run (log book for this run)
with mlflow.start_run():

    # Log hash to MLflow under "data_version" so every model
    # run is linked to a specific dataset version 
    mlflow.log_param("data_version", get_dvc_file_hash())

    # automatically starts run, needs to be within the "with" statement
    mlflow.log_artifact('data/processed/test_data.pkl') 

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