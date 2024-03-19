import csv
import glob
from kafka_producer import send_data_to_kafka
def preprocess_and_send(file_path):
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Send the data we need/ or send all?
            send_data_to_kafka(row)


if __name__ == "__main__":
    # Loop through dataset files and send their data
    directory_path = 'highd-dataset-v1.0/data'
    for file_path in glob.glob(f"{directory_path}/*_tracks.csv"):
        preprocess_and_send(file_path)