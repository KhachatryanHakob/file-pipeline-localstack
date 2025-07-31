import boto3
import time
import os
import requests
import json

print("Starting inspector...")
print(f"AWS_ENDPOINT: {os.getenv('AWS_ENDPOINT', 'http://localstack:4566')}")
print(f"BUCKET_NAME: {os.getenv('BUCKET_NAME', 'localstack-bucket')}")
print(f"QUEUE_NAME: {os.getenv('QUEUE_NAME', 'file-upload-event')}")

sqs = boto3.client('sqs',
    endpoint_url=os.getenv("AWS_ENDPOINT", "http://localstack:4566"),
    region_name="eu-central-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

s3 = boto3.client('s3',
    endpoint_url=os.getenv("AWS_ENDPOINT", "http://localstack:4566"),
    region_name="eu-central-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

bucket_name = os.getenv("BUCKET_NAME", "localstack-bucket")
queue_name = os.getenv("QUEUE_NAME", "file-upload-event")
frontend_url = os.getenv("FRONTEND_NOTIFY_URL", "http://frontend:3000/notify")

print(f"Trying to connect to queue: {queue_name}")

try:
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    print(f"Successfully connected to queue: {queue_url}")
except Exception as e:
    print(f"Error connecting to queue: {e}")
    try:
        queues = sqs.list_queues()
        print(f"Available queues: {queues}")
    except Exception as e2:
        print(f"Error listing queues: {e2}")
    exit(1)

print("Inspector запущен и слушает очередь...")

while True:
    try:
        messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

        if 'Messages' in messages:
            for msg in messages['Messages']:
                print("Получено сообщение:", msg['Body'])

                try:
                    # Parse the JSON message
                    message_data = json.loads(msg['Body'])
                    
                    if 'Records' in message_data:
                        for record in message_data['Records']:
                            if record.get('eventName') == 'ObjectCreated:Put':
                                # Extract file information from S3 event
                                s3_data = record.get('s3', {})
                                object_data = s3_data.get('object', {})
                                
                                key = object_data.get('key', '')
                                size = object_data.get('size', 0)
                                
                                print(f"Извлечённый файл: {key}")
                                print(f"Размер файла {key}: {size} байт")

                                # 🔁 Отправка в frontend
                                data = {
                                    "filename": key,
                                    "size": size
                                }

                                try:
                                    res = requests.post(frontend_url, json=data)
                                    print(f"Уведомление отправлено: {res.status_code}")
                                except Exception as e:
                                    print(f"Ошибка при отправке уведомления: {e}")
                
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON message: {e}")
                except Exception as e:
                    print(f"Error processing message: {e}")

                # Удалим сообщение из очереди
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
        else:
            time.sleep(1)
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(5)
