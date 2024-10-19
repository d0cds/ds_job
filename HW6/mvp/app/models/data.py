from sqlmodel import SQLModel, Field
from typing import Optional, List
from database.database import get_session, engine
import pandas as pd


#  Класс для предоставления исходного датасета
class Data(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name_job: str
    type_busy: str
    qualification: Optional[str]
    location: str
    federalDistrictCode: str
    skills: str
    salary_min: int
    salary_max: int
    salary_stat_mean: int

    class Config:
        protected_namespaces = ()  

    def get_data_all(engine=engine) -> List['Data']:
        # Получить все данные из базы данных напрямую, чтобы быстрее отработатьчем с использованием orm
        data = pd.read_sql('SELECT * FROM data',engine)
        return data


#  Класс для предоставления дополнительных данных
class Dataloc(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location: str
    cod: str
    salary: int

    class Config:
        protected_namespaces = ()  

    def get_data_all(engine=engine) -> List['Data']:
        # Получить все данные из базы данных напрямую, чтобы быстрее отработать чем с использованием orm
        data = pd.read_sql('SELECT * FROM dataloc',engine)
        return data
