import os
import joblib
import logging

logger = logging.getLogger(__name__)

ml_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(ml_dir, "task_priority_model.joblib")

model = None


def load_model():
    global model
    if model is None:
        try:
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                logger.info("Task priority model loaded successfully.")
            else:
                logger.warning(
                    f"Model file not found at {model_path}. Please train the model first."
                )
        except Exception as e:
            logger.error(f"Error loading model: {e}")


def predict_priority(title: str, description: str) -> str:
    if model is None:
        load_model()

    if model is None:
        # Fallback if model cannot be loaded
        return "medium"

    text = f"{title or ''} {description or ''}"
    try:
        prediction = model.predict([text])
        return prediction[0]
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return "medium"
