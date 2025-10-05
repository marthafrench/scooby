echo "Instance name:"
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name

echo "Zone:"
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone

echo "Project:"
gcloud config get-value project
Step 2: Copy those values, then on your local machine run:
bashgcloud compute ssh <INSTANCE_NAME> \
  --project=<PROJECT_ID> \
  --zone=<ZONE> \
  -- -L 8080:localhost:8080
Step 3: Once connected, go back to Workbench and run:
bashcd ~/fastapi-gradio-test
python main.py
Step 4: Open your local browser to: http://localhost:8080
Done! No downloads, no waiting, and it just works. Want to try this instead?
