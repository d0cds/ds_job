from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any
from database.database import get_session
import  services.crud.mlservice as mlservice
from models.user import User as UserModel
from models.mlmodel import MLModel
from webui.auth.dependencies import get_current_user
from models.user import User

router = APIRouter()

class PredictionRequest(BaseModel):
    input_data: Dict

@router.post("/")
def predict(prediction_request: PredictionRequest,
            current_user: User = Depends(get_current_user)):
    with get_session() as session:
        user = session.get(UserModel, current_user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        result = mlservice.process_task(user, prediction_request.input_data)
        return result