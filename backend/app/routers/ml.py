from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from app.models.user import User
from ml.predict import predict_priority
from ml.predict_assignment import predict_assignment

router = APIRouter()


class PredictionRequest(BaseModel):
    title: str
    description: str | None = None


class PredictionResponse(BaseModel):
    priority: str


class PredictionAssignmentResponse(BaseModel):
    department: str
    role: str


@router.post("/predict-priority", response_model=PredictionResponse)
async def predict_task_priority(
    request: PredictionRequest, current_user: User = Depends(get_current_user)
):
    """
    Predicts the task priority based on its title and description.
    Uses the loaded scikit-learn model.
    """
    priority = predict_priority(request.title, request.description)
    return PredictionResponse(priority=priority)


@router.post("/predict-assignment", response_model=PredictionAssignmentResponse)
async def predict_task_assignment(
    request: PredictionRequest, current_user: User = Depends(get_current_user)
):
    """
    Predicts the optimal department and role for a task based on its title and description.
    Uses the loaded scikit-learn multi-output model.
    """
    department, role = predict_assignment(request.title, request.description)
    return PredictionAssignmentResponse(department=department, role=role)
