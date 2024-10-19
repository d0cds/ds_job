from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from database.database import get_session
from models.mltask import MLTask
from webui.auth.dependencies import get_current_user
from models.user import User

router = APIRouter()

@router.get("/")
def get_history(current_user: User = Depends(get_current_user)):
        with get_session() as session:
            task = session.query(MLTask).order_by(MLTask.created_at.desc()).first()
            session.expunge_all()
            if task:
                return task
            return None