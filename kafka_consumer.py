from confluent_kafka import Consumer, KafkaError
import json
import sqlite3
from init_db import *

# Thresholds
ACCELERATION_THRESHOLD = 0.3
THW_THRESHOLD = 1.5
TTC_THRESHOLD = 2

# Data structures to hold vehicle metrics
vehicle_risk_scores = {}


def detect_significant_acceleration(x_acceleration):
    return abs(x_acceleration) > ACCELERATION_THRESHOLD


def detect_tailgating(thw, ttc):
    return thw < THW_THRESHOLD or ttc < TTC_THRESHOLD


def analyze_data(data):
    # Extract necessary information from data
    vehicle_id = data['id']
    x_acceleration = float(data['xAcceleration'])
    thw = float(data['thw'])
    ttc = float(data['ttc'])

    # Initialize vehicle in risk scores dictionary
    vehicle_risk_scores.setdefault(vehicle_id, 'Unknown Risk')

    # Check for threshold crossing
    risk_factor_count = 0

    if detect_significant_acceleration(x_acceleration):
        risk_factor_count += 1
    if detect_tailgating(thw, ttc):
        risk_factor_count += 1

    # Assign a risk score
    if risk_factor_count == 0:
        risk_score = 'Low Risk - Normal driving behaviour'
    elif risk_factor_count == 1:
        risk_score = 'Moderate Risk - Caution advised'
    elif risk_factor_count == 2:
        risk_score = 'High Risk - Immediate action required'

    vehicle_risk_scores[vehicle_id] = risk_score

    conn = sqlite3.connect('../HighDCollisionSimulation/vehicle_risk_scores.db')
    c = conn.cursor()

    # Insert or replace the current score
    c.execute('REPLACE INTO risk_scores (vehicle_id, risk_score) VALUES (?, ?)',
              (vehicle_id, risk_score))
    conn.commit()
    conn.close()


def create_kafka_consumer():
    config = {
        'bootstrap.servers': 'pkc-v12gj.northamerica-northeast2.gcp.confluent.cloud:9092',
        'group.id': 'collision-detection-group',
        'auto.offset.reset': 'earliest',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': 'IYYUQ7PIYMF5WJYL',
        'sasl.password': 'lEIWzSKOFIGLMu0eBeLrzkHM93xxilyetxCekzv9nqO7JEAISaZhYhVU7rdJyKlE',
    }
    return Consumer(**config)


consumer = create_kafka_consumer()
topic_name = 'collision-sim'

consumer.subscribe([topic_name])

try:
    while True:
        msg = consumer.poll(1.0)  # Adjust poll timeout as needed

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        data = json.loads(msg.value().decode('utf-8'))
        analyze_data(data)

finally:
    consumer.close()
