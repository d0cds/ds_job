from sqlmodel import SQLModel, Session, create_engine 
from contextlib import contextmanager
from .config import get_settings

import pandas as pd

engine = create_engine(url=get_settings().DATABASE_URL_psycopg, 
                       echo=True, pool_size=5, max_overflow=10)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        

def insert_data_from_csv(table, path_csv:str):
    data_csv =  pd.read_csv(path_csv,sep="|")
    data_csv.to_sql(table,engine,if_exists='replace', index=False)

def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    insert_data_from_csv(table="data", path_csv="./data/data.csv" )
    insert_data_from_csv(table="dataloc", path_csv="./data/data_location.csv" )