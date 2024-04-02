from confluent_kafka import Producer
import json


def create_kafka_producer():
    config = {
        'bootstrap.servers': 'pkc-v12gj.northamerica-northeast2.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': 'IYYUQ7PIYMF5WJYL',
        'sasl.password': 'lEIWzSKOFIGLMu0eBeLrzkHM93xxilyetxCekzv9nqO7JEAISaZhYhVU7rdJyKlE'
    }
    return Producer(**config)


producer = create_kafka_producer()
topic_name = 'collision-sim'


# function to send data
def send_data_to_kafka(data):
    def acked(err, msg):
        if err is not None:
            print(f"Failed to deliver message: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    try:
        producer.produce(topic_name, json.dumps(data).encode('utf-8'), callback=acked)
    except Exception as e:
        print(f"Failed to send data to Kafka: {e}")
    producer.poll(0)

