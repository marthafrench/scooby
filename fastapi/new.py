import gradio as gr
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app with root_path for proxy support
app = FastAPI(
    title="FastAPI + Gradio Test",
    root_path="/proxy/8080",  # This helps with the proxy
    docs_url="/api/docs",      # Move docs to avoid conflicts
    redoc_url="/api/redoc"
)

# Data model for API
class Message(BaseModel):
    text: str

# FastAPI endpoints
@app.get("/api")
def api_root():
    return {
        "message": "FastAPI is running!", 
        "status": "healthy",
        "endpoints": {
            "health": "/api/health",
            "echo": "/api/echo (POST)",
            "process": "/api/process/{text}",
            "docs": "/api/docs"
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "FastAPI + Gradio"}

@app.post("/api/echo")
def echo_message(msg: Message):
    return {"original": msg.text, "echoed": f"Echo: {msg.text}"}

@app.get("/api/process/{text}")
def api_process_text(text: str):
    """API endpoint to process text"""
    return {"original": text, "processed": text.upper(), "length": len(text)}

# Gradio UI functions
def process_text(text):
    """Simple text processing function for Gradio"""
    print(f"Received text: {text}")
    if not text or text.strip() == "":
        return "Please enter some text!"
    result = f"Processed: {text.upper()}"
    print(f"Returning: {result}")
    return result

def greet(name):
    """Simple greeting function"""
    print(f"Received name: {name}")
    if not name or name.strip() == "":
        return "Please enter your name!"
    result = f"Hello, {name}! FastAPI and Gradio are working together."
    print(f"Returning: {result}")
    return result

# Create Gradio interface
with gr.Blocks(title="FastAPI + Gradio Test") as demo:
    gr.Markdown("# 🚀 FastAPI + Gradio Connectivity Test")
    gr.Markdown("✅ **Both FastAPI and Gradio are running successfully!**")
    
    with gr.Tab("Text Processor"):
        gr.Markdown("### Transform your text to uppercase")
        text_input = gr.Textbox(
            label="Enter text", 
            placeholder="Type something here...",
            lines=2
        )
        text_btn = gr.Button("Process Text", variant="primary")
        text_output = gr.Textbox(label="Result", lines=2)
        
        text_btn.click(
            fn=process_text, 
            inputs=text_input, 
            outputs=text_output
        )
        
        text_input.submit(
            fn=process_text,
            inputs=text_input,
            outputs=text_output
        )
        
        gr.Examples(
            examples=["hello world", "testing gradio", "fastapi rocks"],
            inputs=text_input
        )
    
    with gr.Tab("Greeter"):
        gr.Markdown("### Get a personalized greeting")
        name_input = gr.Textbox(
            label="Your name", 
            placeholder="Enter your name here...",
            lines=1
        )
        greet_btn = gr.Button("Greet Me", variant="primary")
        greet_output = gr.Textbox(label="Greeting", lines=2)
        
        greet_btn.click(
            fn=greet, 
            inputs=name_input, 
            outputs=greet_output
        )
        
        name_input.submit(
            fn=greet,
            inputs=name_input,
            outputs=greet_output
        )
        
        gr.Examples(
            examples=["Alice", "Bob", "Charlie"],
            inputs=name_input
        )
    
    with gr.Tab("API Endpoints"):
        gr.Markdown("""
        ### 📡 Available FastAPI Endpoints
        
        All API endpoints are prefixed with `/api`:
        
        | Method | Endpoint | Description |
        |--------|----------|-------------|
        | GET | `/api` | API information and endpoint list |
        | GET | `/api/health` | Health check |
        | POST | `/api/echo` | Echo back a message |
        | GET | `/api/process/{text}` | Process text (returns uppercase) |
        | GET | `/api/docs` | Interactive API documentation |
        | GET | `/api/redoc` | Alternative API documentation |
        
        ### 🧪 Test the API in your browser:
        
        1. **Health Check**: Add `/api/health` to your current URL
        2. **Process Text**: Add `/api/process/hello` to your current URL
        3. **API Docs**: Add `/api/docs` to your current URL
        
        ### 💻 Test with curl (in terminal):
        
        ```bash
        # Health check
        curl http://localhost:8080/api/health
        
        # Process text
        curl http://localhost:8080/api/process/hello
        
        # Echo endpoint
        curl -X POST http://localhost:8080/api/echo \
          -H "Content-Type: application/json" \
          -d '{"text": "Hello FastAPI"}'
        ```
        
        ### ✅ What this demonstrates:
        
        - FastAPI REST API endpoints ✓
        - Gradio interactive UI ✓
        - Integration between both frameworks ✓
        - Working in Vertex AI Workbench ✓
        """)

# Mount Gradio app to FastAPI at root
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting FastAPI + Gradio server on port 8080")
    print("=" * 70)
    print("📍 Access points:")
    print("   Gradio UI: https://YOUR-INSTANCE.notebooks.googleusercontent.com/proxy/8080/")
    print("   API Info:  https://YOUR-INSTANCE.notebooks.googleusercontent.com/proxy/8080/api")
    print("   API Docs:  https://YOUR-INSTANCE.notebooks.googleusercontent.com/proxy/8080/api/docs")
    print("   Health:    https://YOUR-INSTANCE.notebooks.googleusercontent.com/proxy/8080/api/health")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
