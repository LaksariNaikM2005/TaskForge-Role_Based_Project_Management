import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

ml_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(ml_dir, "assignment_dataset.csv")
model_path = os.path.join(ml_dir, "task_assignment_model.joblib")


def train_assignment_model():
    print("Loading assignment dataset...")
    df = pd.read_csv(dataset_path)

    # Combine title and description for better context
    df["text"] = df["title"].fillna("") + " " + df["description"].fillna("")

    X = df["text"]
    y = df[["department", "role"]]

    print("Splitting data into train, val, and test sets...")
    # First split into train_val (80%) and test (20%)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Then split train_val into train (75% of 80% = 60%) and val (25% of 80% = 20%)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.25, random_state=42
    )

    print(
        f"Dataset split: {len(X_train)} Train, {len(X_val)} Validation, {len(X_test)} Test"
    )

    print("Building model pipeline...")
    # A pipeline using TF-IDF and Logistic Regression wrapped in a MultiOutputClassifier
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(stop_words="english", max_features=1000)),
            ("clf", MultiOutputClassifier(LogisticRegression(max_iter=1000))),
        ]
    )

    print("Training model on train set...")
    pipeline.fit(X_train, y_train)

    print("Evaluating model on validation set...")
    y_val_pred = pipeline.predict(X_val)
    val_accuracy_dept = accuracy_score(y_val["department"], y_val_pred[:, 0])
    val_accuracy_role = accuracy_score(y_val["role"], y_val_pred[:, 1])
    print(
        f"Validation Accuracy - Department: {val_accuracy_dept:.4f}, Role: {val_accuracy_role:.4f}"
    )

    print("\nEvaluating model on test set...")
    y_test_pred = pipeline.predict(X_test)
    test_accuracy_dept = accuracy_score(y_test["department"], y_test_pred[:, 0])
    test_accuracy_role = accuracy_score(y_test["role"], y_test_pred[:, 1])
    print(
        f"Test Accuracy - Department: {test_accuracy_dept:.4f}, Role: {test_accuracy_role:.4f}"
    )

    print("\nTest Classification Report - Department:")
    print(classification_report(y_test["department"], y_test_pred[:, 0]))

    print("\nTest Classification Report - Role:")
    print(classification_report(y_test["role"], y_test_pred[:, 1]))

    print(f"Saving model to {model_path}...")
    joblib.dump(pipeline, model_path)
    print("Model saved successfully.")


if __name__ == "__main__":
    if not os.path.exists(dataset_path):
        print(
            f"Dataset not found at {dataset_path}. Please run generate_assignment_dataset.py first."
        )
    else:
        train_assignment_model()
