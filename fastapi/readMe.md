# FastAPI GCP Connectivity Test

A minimal FastAPI project to test GCP connectivity with a simple UI.

## Features

- ✅ Hello World endpoint
- ✅ Health check endpoint
- ✅ GCP authentication test
- ✅ GCP Storage connectivity test
- ✅ Simple web UI for testing all endpoints

## Setup

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up GCP authentication:**
```bash
# Using service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# OR using gcloud CLI
gcloud auth application-default login
```

3. **Run the application:**
```bash
python main.py
```

4. **Access the UI:**
- Open browser: http://localhost:8080/ui
- API docs: http://localhost:8080/docs

### Deploy to GCP Cloud Run

1. **Build and push Docker image:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/fastapi-gcp-test
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy fastapi-gcp-test \
  --image gcr.io/YOUR_PROJECT_ID/fastapi-gcp-test \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### Deploy to GCP Compute Engine

1. **SSH into your VM**

2. **Install Docker (if not already installed):**
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

3. **Copy files and build:**
```bash
docker build -t fastapi-gcp-test .
```

4. **Run container:**
```bash
docker run -d -p 8080:8080 \
  -v /path/to/service-account.json:/app/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/key.json \
  --name fastapi-test \
  fastapi-gcp-test
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Hello World |
| `/health` | GET | Health check |
| `/gcp/auth` | GET | Test GCP authentication |
| `/gcp/storage` | GET | Test GCP Storage connectivity |
| `/ui` | GET | Web UI for testing |
| `/docs` | GET | Interactive API documentation |

## Testing

Visit `/ui` to access the web interface where you can test all endpoints with one click.

## Project Structure

```
.
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md           # This file
```

## Troubleshooting

**Authentication Issues:**
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Verify service account has necessary permissions
- For Cloud Run, authentication is automatic

**Storage Access Issues:**
- Ensure service account has `storage.buckets.list` permission
- Check if any buckets exist in your project

**Port Issues:**
- Default port is 8080
- Change in `main.py` if needed: `uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)`
