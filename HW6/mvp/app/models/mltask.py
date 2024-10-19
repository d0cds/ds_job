from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List,Dict, Any
from datetime import datetime, timezone
from database.database import get_session


#  Класс задачи ML для представления ML задачи в системе
class MLTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    input_data: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    output_data: Optional[str]
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cost: int

    class Config:
        protected_namespaces = ()  

    @classmethod
    def create(cls, user_id: int, input_data: str, output_data: Optional[str], status: str, cost: int) -> 'MLTask':
        # Создать новую задачу ML в базе данных и вернуть экземпляр задачи
        with get_session() as session:
            ml_task = MLTask(
                user_id=user_id,
                input_data=input_data,
                output_data=output_data,
                status=status,
                cost=cost
            )
            session.add(ml_task)
            session.commit()
            session.refresh(ml_task)

    @classmethod
    def get_user_tasks(cls, user_id: int) -> List['MLTask']:
        # Получить все задачи ML для заданного пользователя из базы данных
        with get_session() as session:
            tasks = session.query(MLTask).filter_by(user_id=user_id).all()
            return tasks
    
    @classmethod
    def get_user_last_task(cls, user_id: int) -> List['MLTask']:
        # Получить последню задачу ML для заданного пользователя из базы данных
        with get_session() as session:
            tasks = session.query(MLTask).filter_by(user_id=user_id).order_by(MLTask.created_at.desc()).first()
            return tasks

