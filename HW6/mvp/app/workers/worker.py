import os
import time
import pika
import json
from models.mlmodel import MLModel
from database.database import get_session
from models.user import User
from models.mltask import MLTask
from database.config import get_settings

settings = get_settings()

# Обработка сообщений из очереди
def callback(ch, method, properties, body):
    # Парсинг JSON сообщения
    task = json.loads(body)
    if True:
        predictions =  MLModel.predict(task["input_data"])
        with get_session() as session:
            # Создание записи о задаче в базе данных
            ml_task = MLTask(
                user_id=int(task["user_id"]),
                input_data=task["input_data"],
                output_data=predictions,
                status="completed",
                cost=int(task["cost"]))

            # Добавление записи в сессию и сохранение изменений
            session.add(ml_task)
            session.commit()


# Установка соединения с RabbitMQ
def connect():
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
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print("Connection to RabbitMQ failed:", e)
            attempts -= 1
            time.sleep(10)
            if attempts == 0:
                raise


connection = connect()
channel = connection.channel()
channel.queue_declare(queue='ml_tasks', durable=True)
channel.basic_consume(queue='ml_tasks', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
