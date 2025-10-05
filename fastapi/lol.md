# Running FastAPI + Gradio in Vertex AI Workbench (Without Proxy)

## Option 1: Using Gradio's Share Feature (Quickest)

This creates a public temporary URL via Gradio's tunneling service.

### Step 1: Create Modified main.py

```bash
# In Terminal
mkdir ~/fastapi-gradio-test
cd ~/fastapi-gradio-test

cat > main.py << 'EOF'
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import threading

# Initialize FastAPI app
app = FastAPI(title="FastAPI + Gradio Test")

class Message(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "FastAPI is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/echo")
def echo_message(msg: Message):
    return {"original": msg.text, "echoed": f"Echo: {msg.text}"}

def process_text(text):
    if not text:
        return "Please enter some text!"
    return f"Processed: {text.upper()}"

def greet(name):
    return f"Hello, {name}! FastAPI and Gradio are working together."

# Create Gradio interface with share=True for public URL
with gr.Blocks(title="FastAPI + Gradio Test") as demo:
    gr.Markdown("# FastAPI + Gradio Connectivity Test")
    gr.Markdown("Running in Vertex AI Workbench with public URL")
    
    with gr.Tab("Text Processor"):
        text_input = gr.Textbox(label="Enter text", placeholder="Type something...")
        text_output = gr.Textbox(label="Output")
        text_btn = gr.Button("Process")
        text_btn.click(fn=process_text, inputs=text_input, outputs=text_output)
    
    with gr.Tab("Greeter"):
        name_input = gr.Textbox(label="Your name", placeholder="Enter your name")
        greet_output = gr.Textbox(label="Greeting")
        greet_btn = gr.Button("Greet Me")
        greet_btn.click(fn=greet, inputs=name_input, outputs=greet_output)

if __name__ == "__main__":
    print("Starting server with Gradio share link...")
    # Launch Gradio with share=True to get public URL
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
EOF

cat > requirements.txt << 'EOF'
gradio==4.8.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
EOF
```

### Step 2: Install and Run

```bash
pip install -r requirements.txt
python main.py
```

**Output will show:**
```
Running on public URL: https://xxxxx.gradio.live
```

Copy that URL and open it in your browser! The link is valid for 72 hours.

---

## Option 2: SSH Port Forwarding (More Secure)

Use SSH tunneling from your local machine to access the Workbench instance.

### Step 1: Get Instance Connection Info

```bash
# In Workbench Terminal, find your instance details
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone
```

### Step 2: Set Up SSH Tunnel (On Your Local Machine)

```bash
# Format:
gcloud compute ssh <instance-name> \
  --project=<your-project-id> \
  --zone=<your-zone> \
  -- -L 8080:localhost:8080

# Example:
gcloud compute ssh my-workbench-instance \
  --project=my-project-123 \
  --zone=us-central1-a \
  -- -L 8080:localhost:8080
```

### Step 3: Run Application (In Workbench)

```bash
python main.py
```

### Step 4: Access Locally

Open on your local machine:
- `http://localhost:8080/ui` - Gradio UI
- `http://localhost:8080/docs` - FastAPI docs

---

## Option 3: Cloud Run Deployment (Production-Ready)

Deploy as a containerized service for permanent access.

### Step 1: Create Dockerfile

```bash
cd ~/fastapi-gradio-test

cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
EOF
```

### Step 2: Update main.py for Cloud Run

```bash
cat > main.py << 'EOF'
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(title="FastAPI + Gradio Test")

class Message(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "FastAPI is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/echo")
def echo_message(msg: Message):
    return {"original": msg.text, "echoed": f"Echo: {msg.text}"}

def process_text(text):
    if not text:
        return "Please enter some text!"
    return f"Processed: {text.upper()}"

def greet(name):
    return f"Hello, {name}! FastAPI and Gradio are working together."

with gr.Blocks(title="FastAPI + Gradio Test") as demo:
    gr.Markdown("# FastAPI + Gradio Connectivity Test")
    
    with gr.Tab("Text Processor"):
        text_input = gr.Textbox(label="Enter text", placeholder="Type something...")
        text_output = gr.Textbox(label="Output")
        text_btn = gr.Button("Process")
        text_btn.click(fn=process_text, inputs=text_input, outputs=text_output)
    
    with gr.Tab("Greeter"):
        name_input = gr.Textbox(label="Your name", placeholder="Enter your name")
        greet_output = gr.Textbox(label="Greeting")
        greet_btn = gr.Button("Greet Me")
        greet_btn.click(fn=greet, inputs=name_input, outputs=greet_output)

app = gr.mount_gradio_app(app, demo, path="/ui")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF
```

### Step 3: Deploy to Cloud Run

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy fastapi-gradio-test \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080

# You'll get a URL like: https://fastapi-gradio-test-xxxxx-uc.a.run.app
```

Access at: `https://your-service-url/ui`

---

## Option 4: Use Vertex AI Endpoint with External IP

If your Workbench instance has an external IP, you can configure firewall rules.

### Step 1: Find External IP

```bash
# In Workbench terminal
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip
```

### Step 2: Create Firewall Rule

```bash
# On your local machine
gcloud compute firewall-rules create allow-gradio \
  --allow tcp:8080 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow Gradio access" \
  --target-tags notebook-instance
```

### Step 3: Run Application

```bash
python main.py
```

### Step 4: Access

`http://<EXTERNAL_IP>:8080/ui`

**Note:** Be cautious with this approach for security reasons.

---

## Recommendation

For quick testing, **use Option 1 (Gradio Share)** - it's the easiest and requires no infrastructure changes.

For regular use, **Option 2 (SSH Port Forwarding)** is secure and reliable.

For production or team access, **Option 3 (Cloud Run)** is the best choice.
