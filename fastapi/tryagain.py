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

@app.get("/api/process/{text}")
def api_process_text(text: str):
    """API endpoint to process text"""
    return {"original": text, "processed": text.upper()}

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
    gr.Markdown("# FastAPI + Gradio Connectivity Test")
    gr.Markdown("**FastAPI is running!** Both the API endpoints and Gradio UI are active.")
    
    with gr.Tab("Text Processor"):
        gr.Markdown("### Test the text processor (Gradio function)")
        text_input = gr.Textbox(
            label="Enter text", 
            placeholder="Type something here...",
            lines=2
        )
        text_btn = gr.Button("Process", variant="primary")
        text_output = gr.Textbox(label="Output", lines=2)
        
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
    
    with gr.Tab("Greeter"):
        gr.Markdown("### Test the greeter (Gradio function)")
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
    
    with gr.Tab("API Info"):
        gr.Markdown("""
        ### FastAPI Endpoints Available:
        
        **GET Endpoints:**
        - `GET /` - Root endpoint (returns status message)
        - `GET /health` - Health check endpoint
        - `GET /api/process/{text}` - Process text via API
        - `GET /docs` - Interactive API documentation (Swagger UI)
        - `GET /redoc` - Alternative API documentation
        
        **POST Endpoints:**
        - `POST /echo` - Echo endpoint (requires JSON: `{"text": "your message"}`)
        
        ### How to Test the API:
        
        1. **Using the browser:** Add `/docs` to your URL to see interactive API docs
        2. **Using curl in terminal:**
        ```bash
        # Test health endpoint
        curl http://localhost:8080/health
        
        # Test echo endpoint
        curl -X POST http://localhost:8080/echo \
          -H "Content-Type: application/json" \
          -d '{"text": "Hello FastAPI"}'
        
        # Test process endpoint
        curl http://localhost:8080/api/process/hello
        ```
        
        3. **From your local machine (if using SSH tunnel):**
        ```bash
        curl http://localhost:8080/health
        ```
        """)

# Mount Gradio app to FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    print("=" * 60)
    print("Starting FastAPI + Gradio server on port 8080")
    print("=" * 60)
    print("Gradio UI: http://localhost:8080/")
    print("FastAPI Docs: http://localhost:8080/docs")
    print("API Endpoints: /health, /echo, /api/process/{text}")
    print("=" * 60)
    print("Use localtunnel in another terminal: lt --port 8080")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
