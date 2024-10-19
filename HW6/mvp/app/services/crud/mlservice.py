import os
import pika
import time
import json
from typing import Dict, Any
from models.user import User
from models.mltask import MLTask
from database.config import get_settings

settings = get_settings()


def process_task(user: User, input_data: Dict):
    # Расчет стоимости выполнения задачи
    cost = 1  # Стоимость 1 запроса
    if not user.subtract_balance(cost):
        return {"status": "fail", "message": "Not balance"}
    task = {
            "user_id": user.id,
            "input_data": input_data,
            "cost": cost
        }

    # Попытка подключения к RabbitMQ с несколькими попытками и задержкой между ними
    attempts = 10
    while attempts > 0:
        try:
            
            print("Attempting to connect to RabbitMQ, attempts left:", attempts)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=int(settings.RABBITMQ_PORT),
                credentials=pika.PlainCredentials(
                        username=settings.RABBITMQ_USER,
                        password=settings.RABBITMQ_PASS),
                heartbeat=30,
                blocked_connection_timeout=2
                ))
            channel = connection.channel()

            channel.queue_declare(queue='ml_tasks', durable=True)

        except pika.exceptions.AMQPConnectionError as e:
            print("Connection to RabbitMQ failed:", e)
            attempts -= 1
            time.sleep(10)
            if attempts == 0:
                raise
               
        channel.basic_publish(exchange='', routing_key='ml_tasks', body=json.dumps(task))

        return {"status": "success", "message": "Task submitted"}
            