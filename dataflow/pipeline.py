import json
from datetime import datetime
import time
import logging
import argparse
import os

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from beam_nuggets.io.kafkaio import KafkaConsume
from beam_nuggets.io import relational_db

# Thresholds
class AnalyzeDoFn(beam.DoFn):
    def process(self, element):
        logging.getLogger().error("******** START")
        data = element
        ACCELERATION_THRESHOLD = 0.3
        THW_THRESHOLD = 1.5
        TTC_THRESHOLD = 2
        
        # Extract necessary information from data
        vehicle_id = data['id']
        x_acceleration = float(data['xAcceleration'])
        thw = float(data['thw'])
        ttc = float(data['ttc'])

        # Check for threshold crossing
        risk_factor_count = 0

        if abs(x_acceleration) > 0.3:
            risk_factor_count += 1
        if thw < THW_THRESHOLD or ttc < TTC_THRESHOLD:
            risk_factor_count += 1

        # Assign a risk score
        if risk_factor_count == 0:
            risk_score = 'Low Risk - Normal driving behaviour'
        elif risk_factor_count == 1:
            risk_score = 'Moderate Risk - Caution advised'
        elif risk_factor_count == 2:
            risk_score = 'High Risk - Immediate action required'

        element = {
            "vehicle_id": vehicle_id,
            "risk_score": risk_score
        }

        return [element]

def run(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--kafkauser', dest='kafkauser', required=True, help='Kafka username')
    parser.add_argument('--kafkapass', dest='kafkapass', required=True, help='Kafka password')
    parser.add_argument('--pghost', dest='pghost', required=True, help='PostgreSQL server')
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = False

    consumer_config = {
        'topic': 'collision-sim',
        'bootstrap_servers': 'pkc-v12gj.northamerica-northeast2.gcp.confluent.cloud:9092',
        'group_id': 'collision-detection-group',
        'auto_offset_reset': 'earliest',
        'security_protocol': 'SASL_SSL',
        'sasl_mechanism': 'PLAIN',
        'sasl_plain_username': known_args.kafkauser,
        'sasl_plain_password': known_args.kafkapass
    }

    db_source_config = relational_db.SourceConfiguration(
        drivername='postgresql+pg8000',
        host=known_args.pghost,
        port=5432,
        username='admin',
        password='adminpassword',
        database='project',
    )

    db_table_config = relational_db.TableConfiguration(
        name='risk_scores',
        create_if_missing=True
    )
    
    with beam.Pipeline(options=pipeline_options) as p:
        messages = (p
            | "Read from Kafka" >> KafkaConsume(consumer_config=consumer_config)
            | "Get Value" >> beam.Map(lambda x: x[1])
            | "Decode JSON" >> beam.Map(lambda x: json.loads(x))
            | "Analyze" >> beam.ParDo(AnalyzeDoFn())
            | 'Writing to DB' >> relational_db.Write(source_config=db_source_config, table_config=db_table_config)
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
