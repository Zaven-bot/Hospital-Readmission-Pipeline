import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import numpy as np
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import argparse

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve,
    accuracy_score
)

from mlflow.sklearn import load_model
from src.feature_engineering import prepare_features

def plot_confusion_matrix(y_true, y_pred, output_path="confusion_matrix.png"):
    cm = confusion_matrix(y_true, y_pred)
    labels = np.unique(y_true)

    fig, ax = plt.subplots(figsize=(6, 5)) #gives control over layout

    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title("Confusion Matrix", fontsize=14)

    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()

    plt.savefig(output_path)
    plt.close()

def plot_roc_curve(y_test, y_probs, output_path="roc_curve.png"):
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    auc = roc_auc_score(y_test, y_probs)
    plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()

    plt.savefig(output_path)
    plt.close()

def evaluate(model, X_test, y_test):
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, output_dict=True)
    y_probs = model.predict_proba(X_test)[:, 1]


    return preds, acc, report, y_probs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a model from MLflow")
    parser.add_argument('--run-id', type=str, default=None) # model from a specific run
    parser.add_argument('--stage', type=str, default="Staging") # 
    parser.add_argument('--model-name', type=str, default="ReadmissionModel") # model name
    parser.add_argument('--run-group', type=str, default=None, help="Group tag for evaluation versioning")
    args = parser.parse_args()

    client = MlflowClient()

    # === Get model version by stage ===
    if args.run_id:
        model_uri = f"runs:/{args.run_id}/random_forest_model"
    else:
        # Fallback: use model from Registry
        latest_version = [
            mv for mv in client.search_model_versions(f"name='{args.model_name}'")
            if mv.current_stage == args.stage
        ][0]
        model_uri = latest_version.source

    # === Load model ===
    model = mlflow.sklearn.load_model(model_uri)

    # === Load test data ===
    X_test, y_test = joblib.load("data/processed/test_data.pkl")

    # === Evaluate ===
    preds, acc, report, y_probs = evaluate(model, X_test, y_test)

    print("\nClassification Report:\n", classification_report(y_test, preds))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, preds))

    mlflow.set_experiment("ReadmissionPipeline")

    # === Start new MLflow run for evaluation ===
    with mlflow.start_run(run_name="Model Evaluation"):

        if args.run_group:
            mlflow.set_tag("run_group", args.run_group)
        if args.run_id:
            mlflow.set_tag("evaluated_run_id", args.run_id)

        # Log metrics
        mlflow.log_metric("eval_accuracy", acc)
        mlflow.log_metric("eval_precision_1", report["1"]["precision"])
        mlflow.log_metric("eval_recall_1", report["1"]["recall"])
        mlflow.log_metric("eval_f1_score_1", report["1"]["f1-score"])

        # Save and log confusion matrix
        rc_path = "roc_curve.png"
        cm_path = "confusion_matrix.png"
        plot_confusion_matrix(y_test, preds, output_path=cm_path)
        plot_roc_curve(y_test, y_probs, output_path=rc_path)
        mlflow.log_artifact(cm_path)
        mlflow.log_artifact(rc_path)

        print(f"\n✅ Evaluation metrics, confusion matrix, and ROC logged to MLflow!")


# if __name__ == "__main__":
#     # Load test data created in train_model.py
#     X_test, y_test = joblib.load('data/processed/test_data.pkl')

#     model = load_model("models:/ReadmissionModel/Production")

#     # Code that was necessary to load the most recently trained model
#     # when I wasn't registering / loading the model.

#     # client = MlflowClient()
#     # latest_run = client.search_runs(experiment_ids=["0"], order_by=["start_time DESC"], max_results=1)[0]
#     # run_id = latest_run.info.run_id
#     # print(run_id, "\nshould be\n", "818df1cfdd2d4812ade2f8c67e1cb259")

#     # model_uri = f"runs:{run_id}/random_forest_model"
#     # model = mlflow.sklearn.load_model(model_uri)

#     evaluate(model, X_test, y_test)
