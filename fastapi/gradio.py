"""
Minimal FastAPI + Gradio test project for Vertex AI Workbench
"""

import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="FastAPI + Gradio Test")

# Data model for API
class Message(BaseModel):
    text: str

# FastAPI endpoints
@app.get("/")
def root():
    return {"message": "FastAPI is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/echo")
def echo_message(msg: Message):
    return {"original": msg.text, "echoed": f"Echo: {msg.text}"}

# Gradio UI functions
def process_text(text):
    """Simple text processing function for Gradio"""
    if not text:
        return "Please enter some text!"
    return f"Processed: {text.upper()}"

def greet(name):
    """Simple greeting function"""
    return f"Hello, {name}! FastAPI and Gradio are working together."

# Create Gradio interface
with gr.Blocks(title="FastAPI + Gradio Test") as demo:
    gr.Markdown("# FastAPI + Gradio Connectivity Test")
    gr.Markdown("Testing basic functionality in Vertex AI Workbench")
    
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
    
    with gr.Tab("API Info"):
        gr.Markdown("""
        ### Available FastAPI Endpoints:
        - `GET /` - Root endpoint
        - `GET /health` - Health check
        - `POST /echo` - Echo endpoint (requires JSON: {"text": "your message"})
        - `GET /docs` - Interactive API documentation
        """)

# Mount Gradio app to FastAPI
app = gr.mount_gradio_app(app, demo, path="/ui")

if __name__ == "__main__":
    print("Starting FastAPI + Gradio server...")
    print("FastAPI docs: http://localhost:8000/docs")
    print("Gradio UI: http://localhost:8000/ui")
    uvicorn.run(app, host="0.0.0.0", port=8000)
