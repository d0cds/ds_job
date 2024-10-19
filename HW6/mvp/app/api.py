from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_analytics.fastapi import Analytics
from routes import user, prediction, balance, history
from database.database import init_db
import uvicorn
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database initialized")
    logger.info("ML models loaded")

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
app.include_router(balance.router, prefix="/balance", tags=["balance"])
app.include_router(history.router, prefix="/history", tags=["history"])

@app.get("/")
async def root():
    return {"message": "Welcome to the ML Service API"}

if __name__ == "__main__":
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)