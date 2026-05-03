import os
import joblib

ml_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(ml_dir, "task_assignment_model.joblib")

# Load the model once when the module is imported
try:
    assignment_model = joblib.load(model_path)
except FileNotFoundError:
    assignment_model = None
    print(
        "Warning: task_assignment_model.joblib not found. Run train_assignment.py first."
    )


def predict_assignment(title: str, description: str = None) -> tuple[str, str]:
    """
    Predicts the task department and role based on title and description.
    Returns a tuple of (department, role).
    """
    if assignment_model is None:
        return "Unknown", "Unknown"

    text = title
    if description:
        text += " " + description

    prediction = assignment_model.predict([text])[0]
    # The MultiOutputClassifier returns an array like ['Engineering', 'employee']
    department = prediction[0]
    role = prediction[1]

    return department, role
