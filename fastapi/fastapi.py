from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
from google.auth import default
import os
from datetime import datetime

app = FastAPI(title="GCP Connectivity Test")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Simple hello world endpoint"""
    return {
        "message": "Hello World from FastAPI!",
        "timestamp": datetime.now().isoformat(),
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fastapi-gcp-test",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/gcp/auth")
async def check_gcp_auth():
    """Check GCP authentication"""
    try:
        credentials, project = default()
        return {
            "status": "authenticated",
            "project_id": project,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth failed: {str(e)}")

@app.get("/gcp/storage")
async def check_gcp_storage():
    """Test GCP Storage connectivity"""
    try:
        client = storage.Client()
        buckets = list(client.list_buckets(max_results=5))
        return {
            "status": "connected",
            "bucket_count": len(buckets),
            "buckets": [b.name for b in buckets],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage check failed: {str(e)}")

@app.get("/ui", response_class=HTMLResponse)
async def get_ui():
    """Simple UI for testing endpoints"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GCP Connectivity Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4285f4;
                margin-bottom: 30px;
            }
            .test-button {
                background: #4285f4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                margin: 10px 5px;
                font-size: 14px;
            }
            .test-button:hover {
                background: #3367d6;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 4px;
                background: #f8f9fa;
                border-left: 4px solid #4285f4;
            }
            .success {
                border-left-color: #34a853;
                background: #e6f4ea;
            }
            .error {
                border-left-color: #ea4335;
                background: #fce8e6;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 GCP Connectivity Test Dashboard</h1>
            <div>
                <button class="test-button" onclick="testEndpoint('/')">Test Hello World</button>
                <button class="test-button" onclick="testEndpoint('/health')">Test Health</button>
                <button class="test-button" onclick="testEndpoint('/gcp/auth')">Test GCP Auth</button>
                <button class="test-button" onclick="testEndpoint('/gcp/storage')">Test GCP Storage</button>
            </div>
            <div id="result"></div>
        </div>

        <script>
            async function testEndpoint(endpoint) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<div class="result">Testing...</div>';
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    const className = response.ok ? 'result success' : 'result error';
                    resultDiv.innerHTML = `
                        <div class="${className}">
                            <strong>Endpoint:</strong> ${endpoint}<br>
                            <strong>Status:</strong> ${response.status}<br>
                            <strong>Response:</strong>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <strong>Error:</strong> ${error.message}
                        </div>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
