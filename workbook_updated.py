import json
import time
import threading
import os
from datetime import datetime
from collections import deque
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain.tools import tool
from langchain.agents import AgentType, initialize_agent
from typing import Callable, Optional, List, Any, Dict
from pydantic import Field
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings

# Set environment variable
os.environ['CONSENT'] = "AGREE"

# Global log store for in-memory logs
log_store = deque(maxlen=1000)  # Keep last 1000 logs
error_logs = deque(maxlen=100)   # Keep last 100 error logs

class ControlPlaneLLM(LLM):
    endpoint_name: str = Field(default="gemini_20_flash")
    model_params: Optional[Dict[str, Any]] = Field(default_factory=lambda: {
        "max_output_tokens": 1024,
        "temperature": 1,
        "top_p": 0.95
    })
    pii_filter: bool = Field(default=True)
    display_output: bool = Field(default=False)

    @property
    def _llm_type(self) -> str:
        return "control_plane_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Mock implementation - replace with actual control plane call
        try:
            import control_plane.llm_package.models as cp
            params = {
                "endpoint_name": self.endpoint_name,
                "prompt": prompt,
                "model_params": self.model_params,
                "pii_filter": self.pii_filter,
                "display_output": self.display_output
            }
            response = cp.invoke_model(config=params)
            return response["content"]
        except ImportError:
            # Fallback for demo purposes
            return f"AI Analysis: This appears to be a {prompt[:50]}... error. Recommended actions: 1. Check system resources 2. Verify configuration 3. Restart affected services"

class ControlPlaneEmbeddings(Embeddings):
    def __init__(self, endpoint_name="textembedding4", display_output=False):
        self.endpoint_name = endpoint_name
        self.display_output = display_output

    def embed_documents(self, texts):
        try:
            import control_plane.llm_package.models as cp
            response = cp.invoke_embedding_model({
                "endpoint_name": self.endpoint_name,
                "texts": texts,
                "display_output": self.display_output
            })
            return [emb.values for emb in response["embeddings"]]
        except ImportError:
            # Mock embeddings for demo
            return [[0.1] * 384 for _ in texts]

    def embed_query(self, text):
        return self.embed_documents([text])[0]

@tool
def fetch_context_logs(correlation_id: str) -> str:
    """Fetch logs from in-memory stream by correlation ID."""
    global log_store
    matching_logs = [log for log in log_store if log.get("correlation_id") == correlation_id]
    if not matching_logs:
        return f"No logs found for correlation ID: {correlation_id}"
    return "\n".join(log.get("stack_trace", "") for log in matching_logs)

@tool
def get_ai_recommendations(error_message: str) -> str:
    """Get fix recommendations using AI analysis."""
    # Create a simple prompt for error analysis
    prompt = f"""
    Analyze this error and provide 3 specific recommendations:
    Error: {error_message}
    
    Provide:
    1. Root cause analysis
    2. Immediate fix steps
    3. Prevention measures
    """

    # Mock AI response for demo
    return f"""
    Root Cause: {error_message[:100]}...
    
    Recommendations:
    1. Check application logs for stack traces
    2. Verify database connections and network connectivity
    3. Restart the affected service if necessary
    
    Prevention:
    1. Implement proper error handling
    2. Add monitoring and alerting
    3. Regular system health checks
    """

@tool
def analyse_log(log_json: str) -> str:
    """Analyse each incoming log and store in memory."""
    global log_store, error_logs

    try:
        log = json.loads(log_json) if isinstance(log_json, str) else log_json
    except json.JSONDecodeError:
        return "Invalid JSON format"

    # Store in memory
    log_store.append(log)

    timestamp = datetime.now().strftime("%H:%M:%S")
    result = f"[{timestamp}] [{log.get('level', 'INFO')}] {log.get('application', 'Unknown')}: {log.get('stack_trace', 'No stack trace')}"

    # If it's an error, analyze it with AI
    if log.get('level') in ['ERROR', 'CRITICAL']:
        error_logs.append(log)
        print(f"Error detected! Analysing with AI...")

        # Get AI recommendations
        recommendations = get_ai_recommendations(log.get('stack_trace', ''))

        analysis = f"""
AI ANALYSIS:
Application: {log.get('application', 'Unknown')}
Issue: {log.get('stack_trace', 'No details')}
Fix Recommendations:
{recommendations}
{"=" * 60}
"""
        print(analysis)
        result += f"\n{analysis}"

    return result

# Agent Prompt Template
agent_prompt = PromptTemplate(
    input_variables=["application", "level", "message", "user_id", "correlation_id", "context_logs"],
    template="""You are Scooby, an expert Site Reliability Engineer (SRE) AI agent specializing in automated incident response.

Your mission: Analyse system logs, identify incidents, and provide actionable resolution guidance with high accuracy.

**Your Capabilities:**
- Parse and analyse system logs from multiple sources
- Search historical incidents for similar patterns
- Check service dependencies and health status
- Generate comprehensive incident response reports

**Analysis Framework:**
1. **Parse Logs**: Structure raw log data for analysis
2. **Classify Severity**: Determine incident priority level
3. **Root Cause Analysis**: Identify primary and contributing factors
4. **Search History**: Find similar past incidents and resolutions
5. **Dependency Check**: Assess affected services and dependencies
6. **Generate Report**: Create actionable incident response documentation

**Available Tools:** {tools}

**Tool Usage Guidelines:**
- Always start by parsing raw logs into structured format
- Search for similar incidents to leverage past resolutions
- Check dependencies to understand full impact scope
- Generate comprehensive reports for incident documentation

**Response Format:**
- Be concise but thorough in your analysis
- Provide specific, actionable recommendations
- Cite specific log entries as evidence
- Focus on minimizing mean time to resolution (MTTR)

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

# Initialize LLM and tools
cp_llm = ControlPlaneLLM()
tools = [fetch_context_logs, get_ai_recommendations, analyse_log]

# Initialize agent
agent_executor = initialize_agent(
    tools=tools,
    llm=cp_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Simple Log Pusher
_current_pusher = None

def push_logs_from_json_simple(json_file_path: str, callback: Optional[Callable] = None, interval_seconds: int = 60):
    """
    Simple function that pushes one log per minute from JSON file until empty.
    Runs in background thread so it doesn't block.

    Args:
        json_file_path: Path to JSON file with logs
        callback: Optional function to call with each log (if None, just prints)
        interval_seconds: Seconds between logs (default: 60 = 1 minute)

    Returns:
        Dictionary with control functions: stop(), status(), logs_remaining()
    """
    global _current_pusher

    # Stop any existing pusher
    if _current_pusher and _current_pusher.running:
        _current_pusher.stop()

    # Load logs from JSON file
    try:
        with open(json_file_path, 'r') as f:
            logs = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return None

    if not logs:
        print("No logs found in file")
        return None

    # State variables
    state = {
        'logs': logs,
        'current_index': 0,
        'running': True,
        'thread': None,
        'callback': callback,
        'interval': interval_seconds
    }

    def push_loop():
        while state['running'] and state['current_index'] < len(logs):
            # Get current log
            current_log = logs[state['current_index']].copy()
            current_log['timestamp'] = datetime.utcnow().isoformat() + 'Z'

            # Process the log
            if callback:
                callback(current_log)
            else:
                # Default: just print it
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Processing log:")
                print(f"  timestamp: {current_log['timestamp']}")
                print(f"  correlation_id: {current_log['correlation_id']}")
                print(f"  app: {current_log['application']}")
                print(f"  user_id: {current_log['user_id']}")
                print(f"  level: {current_log['level']}")
                print(f"  message: {current_log['stack_trace']}")

                # Analyze the log
                analyse_log(current_log)

            state['current_index'] += 1

            # Check if done
            if state['current_index'] >= len(logs):
                state['running'] = False
                break

            # Wait for next interval
            if state['running']:
                time.sleep(interval_seconds)

    # Start background thread
    state['thread'] = threading.Thread(target=push_loop, daemon=False)
    state['thread'].start()

    # Create control object
    class PusherControl:
        def __init__(self, state):
            self._state = state

        def stop(self):
            self._state['running'] = False

        def wait_for_completion(self, check_interval: int = 10):
            """Wait for all logs to be pushed (blocking)"""
            while self._state['running']:
                time.sleep(check_interval)
                remaining = len(logs) - self._state['current_index']
                if remaining > 0:
                    print(f"Status: {self._state['current_index']}/{len(logs)} complete, {remaining} remaining")

        @property
        def running(self):
            return self._state['running']

    control = PusherControl(state)
    _current_pusher = control
    return control

def stop_current_pusher():
    """Stop any currently running pusher"""
    global _current_pusher
    if _current_pusher and _current_pusher.running:
        _current_pusher.stop()
        _current_pusher = None

def create_sample_json(filename: str = "sample_logs.json"):
    """Create a sample JSON file for testing"""
    sample_logs = [
        {
            "timestamp": "2025-07-10 08:45:01,212",
            "level": "ERROR",
            "application": "payments-application",
            "user_id": "45da6094-3283-49a6-a43d-2af72ef198bb",
            "correlation_id": "abc123def4",
            "stack_trace": "2025-07-10 08:45:01,123 - ERROR - correlation_id: abc123def4: Database connection failed - Connection timeout after 30 seconds"
        },
        {
            "timestamp": "2025-07-10 09:01:12,114",
            "level": "ERROR",
            "application": "payments-application",
            "user_id": "45da6094-3283-49a6-a43d-2af72ef198bb",
            "correlation_id": "bd45ef67c2",
            "stack_trace": "2025-07-10 09:01:12,105 - ERROR - correlation_id: bd45ef67c2: Payment processing failed - Invalid card number format"
        },
        {
            "timestamp": "2025-07-10 09:15:33,445",
            "level": "CRITICAL",
            "application": "auth-service",
            "user_id": "12345678-1234-5678-9012-123456789012",
            "correlation_id": "critical123",
            "stack_trace": "2025-07-10 09:15:33,440 - CRITICAL - correlation_id: critical123: Memory usage exceeded 95% - Service becoming unresponsive"
        }
    ]

    with open(filename, 'w') as f:
        json.dump(sample_logs, f, indent=2)
    return filename

def run_agent_analysis(input_text: str):
    """Run the agent with given input"""
    try:
        result = agent_executor.run(input_text)
        return result
    except Exception as e:
        return f"Agent error: {str(e)}"

# Main execution
if __name__ == "__main__":
    print("Starting AI Log Analysis Agent...")

    # Create sample data first
    sample_file = create_sample_json('demo_logs.json')
    print(f"Created sample file: {sample_file}")

    # Start the log pusher (processes 1 log every 10 seconds for demo)
    pusher = push_logs_from_json_simple('demo_logs.json', interval_seconds=10)

    if pusher:
        print("Log pusher started. Processing logs...")

        # Wait for completion or stop after 1 minute for demo
        try:
            time.sleep(60)  # Let it run for 1 minute
        except KeyboardInterrupt:
            print("\nStopping...")

        pusher.stop()
        print("Log pusher stopped.")

        # Example of using the agent directly
        print("\n" + "="*60)
        print("Example Agent Analysis:")
        result = run_agent_analysis("Analyze the recent error logs and provide recommendations")
        print(result)
    else:
        print("Failed to start log pusher")