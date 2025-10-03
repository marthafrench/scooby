from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="FastAPI Hello World")

@app.get("/")
async def hello_world():
    """Simple hello world endpoint"""
    return {
        "message": "Hello World from FastAPI!",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ui", response_class=HTMLResponse)
async def get_ui():
    """Simple UI to display hello world"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Hello World</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
            }
            button:hover {
                background: #5568d3;
            }
            #message {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                display: none;
            }
            .response {
                font-size: 24px;
                color: #667eea;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .timestamp {
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 FastAPI on GCP</h1>
            <p>Click the button to fetch Hello World from the API</p>
            <button onclick="fetchHelloWorld()">Get Hello World</button>
            <div id="message"></div>
        </div>

        <script>
            async function fetchHelloWorld() {
                const messageDiv = document.getElementById('message');
                messageDiv.style.display = 'block';
                messageDiv.innerHTML = '<p>Loading...</p>';
                
                try {
                    const response = await fetch('/');
                    const data = await response.json();
                    
                    messageDiv.innerHTML = `
                        <div class="response">${data.message}</div>
                        <div class="timestamp">Timestamp: ${data.timestamp}</div>
                    `;
                } catch (error) {
                    messageDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
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
