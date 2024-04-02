Before running:
* Create a kafka topic named `collision-sim`
* Generate kafka API keys (username and password)
* Get repo path from Google Cloud.

Run the commands below in the extracted zip folder on the Google Cloud console.

```
REPO=<REPO path from milestone 4>
PROJECT=$(gcloud config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-bucket

cd k8s/postgres
POSTGRES_IMAGE=$REPO/postgres:project
gcloud builds submit -t $POSTGRES_IMAGE

cd ../dashboard
DASHBOARD_IMAGE=$REPO/dashboard
gcloud builds submit -t $DASHBOARD_IMAGE

cd ..
POSTGRES_IMAGE=$POSTGRES_IMAGE DASHBOARD_IMAGE=$DASHBOARD_IMAGE envsubst < project.yaml | kubectl apply -f -

kubectl get services

# wait until external IPs are provided
# use the external IP for postgres below

cd ../dataflow

python pipeline.py \
   --runner DataflowRunner \
   --project $PROJECT \
   --region  northamerica-northeast2 \
   --experiment use_unsupported_python_version \
   --streaming \
   --requirements requirements.txt \
   --staging_location $BUCKET/staging \
   --temp_location $BUCKET/temp \
   --kafkauser <kafka username> \
   --kafkapass <kafka password> \
   --pghost <postgres IP>
```

Be sure to place `highd-dataset-v1.0` into the `local` folder.

Then, run the following below in the extracted zip folder on your local machine.


```
pip3 install confluent-kafka confluent-kafka configparse

cd local
python3 preprocessing.py
```

Visit the` dashboard` external IP in a web browser to see the dashboard.
