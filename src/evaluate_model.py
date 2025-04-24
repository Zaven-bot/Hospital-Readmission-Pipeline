import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve,
    accuracy_score
)

from mlflow.sklearn import load_model
import mlflow.sklearn
from src.feature_engineering import prepare_features

def plot_confusion(y_test, y_pred, labels=[0,1]):
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(6, 5)) #gives control over layout

    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title("Confusion Matrix", fontsize=14)

    # Add axis titles manually to simulate "True / Predicted" labels above and beside the heatmap
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()

    plt.show()

def plot_roc_curve(y_test, y_probs):
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    auc = roc_auc_score(y_test, y_probs)
    plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.show()

def evaluate(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_probs = model.predict_proba(X_test)[:, 1]

    print("\n✅ Accuracy:", accuracy_score(y_test, y_pred))
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    plot_confusion(y_test, y_pred)
    plot_roc_curve(y_test, y_probs)

if __name__ == "__main__":
    # Load test data created in train_model.py
    X_test, y_test = joblib.load('data/processed/test_data.pkl')

    model = load_model("models:/ReadmissionModel/Production")

    # Code that was necessary to load the most recently trained model
    # when I wasn't registering / loading the model.

    # client = MlflowClient()
    # latest_run = client.search_runs(experiment_ids=["0"], order_by=["start_time DESC"], max_results=1)[0]
    # run_id = latest_run.info.run_id
    # print(run_id, "\nshould be\n", "818df1cfdd2d4812ade2f8c67e1cb259")

    # model_uri = f"runs:{run_id}/random_forest_model"
    # model = mlflow.sklearn.load_model(model_uri)



    evaluate(model, X_test, y_test)
