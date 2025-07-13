# Cell 1: Initializing Variables and Imports
"""
🐕 Simple Scooby AI - Log Analysis with LangChain + Gemini 2.0 Flash
Analyzes logs and provides fix recommendations
"""

import json
import time
import threading
import os
from datetime import datetime
from collections import deque

# LangChain imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain imports successful")
except ImportError:
    print("❌ Install: pip install langchain langchain-google-genai")
    LANGCHAIN_AVAILABLE = False

# Configuration variables
API_KEY = os.getenv('GOOGLE_API_KEY')
MAX_RECENT_LOGS = 100
MAX_ERROR_LOGS = 20
MODEL_NAME = "gemini-2.0-flash-exp"
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 500

# Initialize data structures
recent_logs = deque(maxlen=MAX_RECENT_LOGS)
error_logs = deque(maxlen=MAX_ERROR_LOGS)

print("🔧 Variables initialized")
print(f"📊 Recent logs buffer: {MAX_RECENT_LOGS}")
print(f"🚨 Error logs buffer: {MAX_ERROR_LOGS}")
print(f"🤖 Model: {MODEL_NAME}")
print(f"🔑 API Key available: {bool(API_KEY)}")

# Cell 2: Loading the Model
"""
Initialize the Gemini 2.0 Flash model via LangChain
"""

# Check prerequisites
if not API_KEY:
    print("❌ Please set GOOGLE_API_KEY environment variable")
    print("   import os")
    print("   os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'")
    raise ValueError("Missing API key")

if not LANGCHAIN_AVAILABLE:
    print("❌ LangChain not available")
    raise ImportError("LangChain not installed")

# Initialize the LLM
try:
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=API_KEY,
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS
    )

    print("✅ Gemini 2.0 Flash model loaded successfully")
    print(f"🤖 Model: {MODEL_NAME}")
    print(f"🌡️ Temperature: {TEMPERATURE}")
    print(f"📝 Max tokens: {MAX_OUTPUT_TOKENS}")

    # Test the model with a simple query
    test_response = llm.invoke([HumanMessage(content="Hello, are you working?")])
    print(f"🧪 Test response: {test_response.content[:50]}...")

except Exception as e:
    print(f"❌ Failed to load model: {e}")
    raise


# Cell 3: Defining Prompt Template
"""
Create the prompt template for log analysis
"""

# Define the prompt template for error analysis
prompt_template = PromptTemplate(
    input_variables=["application", "level", "message", "user_id", "correlation_id", "context_logs"],
    template="""You are a Site Reliability Engineer. Analyze this error log and provide 3 specific, actionable fix recommendations.

ERROR LOG:
Application: {application}
Level: {level}
Message: {message}
User: {user_id}
Correlation ID: {correlation_id}

RECENT CONTEXT (last few logs):
{context_logs}

Provide exactly 3 specific, actionable recommendations to fix this issue. Be concise and practical.
Focus on immediate actions that an engineer can take right now.

Format your response as:
1. [First recommendation]
2. [Second recommendation] 
3. [Third recommendation]"""
)

print("✅ Prompt template created")
print("📝 Template variables:", prompt_template.input_variables)
print("🎯 Template focuses on: SRE analysis with actionable recommendations")

# Test the template formatting
sample_format = prompt_template.format(
    application="test-service",
    level="ERROR",
    message="Database connection failed",
    user_id="user_123",
    correlation_id="req_abc",
    context_logs="[INFO] Service started\n[WARN] High memory usage"
)

print("\n🧪 Sample formatted prompt (first 200 chars):")
print(sample_format[:200] + "...")

# Cell 4: Creating the LangChain Chain
"""
Create the LangChain chain that combines the model and prompt template
"""

# Create the LangChain chain
try:
    # Create the chain combining prompt template and LLM
    analysis_chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        verbose=False  # Set to True for debugging
    )

    print("✅ LangChain analysis chain created")
    print("🔗 Chain components:")
    print(f"   - LLM: {MODEL_NAME}")
    print(f"   - Prompt: SRE Log Analysis Template")
    print(f"   - Input variables: {prompt_template.input_variables}")

    # Test the chain with sample data
    test_result = analysis_chain.run(
        application="test-app",
        level="ERROR",
        message="Connection timeout to database",
        user_id="test_user",
        correlation_id="test_123",
        context_logs="[INFO] App started\n[WARN] Slow queries detected"
    )

    print("\n🧪 Test chain execution successful")
    print(f"📄 Sample output (first 100 chars): {test_result[:100]}...")

except Exception as e:
    print(f"❌ Failed to create chain: {e}")
    raise


# Helper function to run the chain
def analyze_with_chain(error_log, context_logs=""):
    """
    Analyze an error log using the LangChain chain

    Args:
        error_log (dict): Log entry with level, application, message, etc.
        context_logs (str): Recent logs for context

    Returns:
        str: AI analysis response
    """
    try:
        response = analysis_chain.run(
            application=error_log.get('application', 'unknown'),
            level=error_log.get('level', 'ERROR'),
            message=error_log.get('message', ''),
            user_id=error_log.get('user_id', 'unknown'),
            correlation_id=error_log.get('correlation_id', 'unknown'),
            context_logs=context_logs
        )
        return response
    except Exception as e:
        return f"Chain execution failed: {e}"


print("🔧 Helper function 'analyze_with_chain' defined")

# Cell 5: The Log Parser
"""
Log parsing and analysis functions
"""


def format_context_logs(logs):
    """Format recent logs for context"""
    if not logs:
        return "No recent logs"

    context = ""
    for log in logs[-5:]:  # Just last 5 for context
        context += f"[{log['level']}] {log['application']}: {log['message']}\n"
    return context.strip()


def parse_recommendations(response_text):
    """Parse recommendations from LangChain response"""
    try:
        lines = response_text.strip().split('\n')
        recommendations = []

        for line in lines:
            line = line.strip()
            # Look for numbered recommendations
            if line and (line[0].isdigit() or '1.' in line or '2.' in line or '3.' in line):
                # Remove numbering and clean up
                if '.' in line:
                    rec = line.split('.', 1)[-1].strip()
                else:
                    rec = line

                if rec and len(rec) > 5:  # Must be substantial
                    recommendations.append(rec)

        # Fallback if parsing fails
        if not recommendations:
            # Try to split by numbers or bullet points
            if '1.' in response_text:
                parts = response_text.split('1.')[1].split('2.')
                if len(parts) > 1:
                    recommendations.append(parts[0].strip())
                    if '3.' in parts[1]:
                        part2, part3 = parts[1].split('3.', 1)
                        recommendations.append(part2.strip())
                        recommendations.append(part3.strip())
                    else:
                        recommendations.append(parts[1].strip())

            if not recommendations:
                recommendations = [response_text.strip()]

        return recommendations[:3]  # Max 3 recommendations

    except Exception as e:
        return [f"Could not parse AI response: {e}"]


def analyze_log(log):
    """Analyze each incoming log"""
    global recent_logs, error_logs

    # Store in memory
    recent_logs.append(log)

    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 📥 [{log['level']}] {log['application']}: {log['message']}")

    # If it's an error, analyze it with AI
    if log['level'] in ['ERROR', 'CRITICAL']:
        error_logs.append(log)
        print(f"🚨 Error detected! Analyzing with Gemini 2.0 Flash...")

        # Get context from recent logs
        context_logs = format_context_logs(list(recent_logs))

        # Get AI recommendations using the chain
        ai_response = analyze_with_chain(log, context_logs)
        recommendations = parse_recommendations(ai_response)

        print(f"\n🤖 AI ANALYSIS:")
        print(f"📱 Application: {log['application']}")
        print(f"🔍 Issue: {log['message']}")
        print(f"💡 Fix Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        print("=" * 60)

        return recommendations

    return None


def get_analysis_status():
    """Get current analysis status"""
    return {
        'total_logs_analyzed': len(recent_logs),
        'error_logs_found': len(error_logs),
        'langchain_available': LANGCHAIN_AVAILABLE and bool(API_KEY),
        'recent_errors': len([log for log in recent_logs if log['level'] in ['ERROR', 'CRITICAL']])
    }


# Sample log creation function for testing
def create_sample_log(app='test-app', level='INFO', message='Test message', user_id='user_123'):
    """Create a sample log entry"""
    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'level': level,
        'application': app,
        'user_id': user_id,
        'correlation_id': f'req_{app}_{int(time.time())}',
        'message': message
    }


print("✅ Log parser functions defined")
print("🔧 Available functions:")
print("   - analyze_log(log): Main analysis function")
print("   - format_context_logs(logs): Format context")
print("   - parse_recommendations(text): Parse AI output")
print("   - get_analysis_status(): Get current status")
print("   - create_sample_log(): Create test logs")

# Cell 6: Main Analysis Function
"""
Main function that analyzes logs and creates recommendations
"""


def run_log_analysis_demo():
    """
    Run a demonstration of the log analysis system
    """
    print("🐕 Simple Scooby AI - Log Analysis Demo")
    print("=" * 60)

    # Create sample error logs for demonstration
    sample_logs = [
        create_sample_log('payment-gateway', 'INFO', 'Payment service started successfully'),
        create_sample_log('payment-gateway', 'WARN', 'High memory usage detected: 85%'),
        create_sample_log('payment-gateway', 'ERROR',
                          'Database connection timeout after 30 seconds - connection pool exhausted'),
        create_sample_log('user-auth', 'ERROR', 'JWT token validation failed - Redis cache unavailable'),
        create_sample_log('notification-service', 'CRITICAL', 'Service completely down - all health checks failing'),
        create_sample_log('api-gateway', 'INFO', 'Request processed successfully'),
    ]

    print(f"📊 Processing {len(sample_logs)} sample logs...")
    print()

    # Process each log
    for i, log in enumerate(sample_logs):
        print(f"\n--- Processing Log {i + 1}/{len(sample_logs)} ---")
        recommendations = analyze_log(log)

        # Add delay between logs for realistic simulation
        if i < len(sample_logs) - 1:
            time.sleep(2)  # Wait 2 seconds between logs

    # Show final status
    status = get_analysis_status()
    print(f"\n📊 ANALYSIS COMPLETE:")
    print(f"   Total logs processed: {status['total_logs_analyzed']}")
    print(f"   Errors found: {status['error_logs_found']}")
    print(f"   Recent errors: {status['recent_errors']}")
    print(f"   AI system ready: {status['langchain_available']}")


def analyze_custom_log(application, level, message, user_id='unknown'):
    """
    Analyze a custom log entry

    Args:
        application (str): Application name
        level (str): Log level (INFO, WARN, ERROR, CRITICAL)
        message (str): Log message
        user_id (str): User ID (optional)

    Returns:
        list: Recommendations if error, None otherwise
    """
    custom_log = create_sample_log(application, level, message, user_id)
    return analyze_log(custom_log)


def batch_analyze_logs(log_list, delay_seconds=1):
    """
    Analyze a batch of logs with optional delay

    Args:
        log_list (list): List of log dictionaries
        delay_seconds (float): Delay between log processing

    Returns:
        dict: Summary of analysis results
    """
    results = {
        'total_processed': 0,
        'errors_found': 0,
        'recommendations_generated': 0
    }

    print(f"🔄 Batch processing {len(log_list)} logs...")

    for i, log in enumerate(log_list):
        print(f"\nProcessing {i + 1}/{len(log_list)}...")
        recommendations = analyze_log(log)

        results['total_processed'] += 1
        if log['level'] in ['ERROR', 'CRITICAL']:
            results['errors_found'] += 1
            if recommendations:
                results['recommendations_generated'] += 1

        if delay_seconds > 0 and i < len(log_list) - 1:
            time.sleep(delay_seconds)

    print(f"\n✅ Batch analysis complete:")
    print(f"   Processed: {results['total_processed']} logs")
    print(f"   Errors: {results['errors_found']}")
    print(f"   Recommendations: {results['recommendations_generated']}")

    return results


# Interactive functions for Jupyter notebook use
def quick_error_analysis(app_name, error_message):
    """Quick analysis of a single error"""
    print(f"🔍 Quick Analysis: {app_name}")
    return analyze_custom_log(app_name, 'ERROR', error_message)


def show_current_status():
    """Display current analysis status"""
    status = get_analysis_status()
    print("📊 Current Status:")
    print(f"   Logs in buffer: {status['total_logs_analyzed']}")
    print(f"   Error logs: {status['error_logs_found']}")
    print(f"   Recent errors: {status['recent_errors']}")
    print(f"   AI ready: {status['langchain_available']}")
    return status


print("✅ Main analysis functions ready")
print("🚀 Available functions:")
print("   - run_log_analysis_demo(): Run full demo")
print("   - analyze_custom_log(app, level, message): Analyze single log")
print("   - batch_analyze_logs(log_list): Process multiple logs")
print("   - quick_error_analysis(app, error): Quick error check")
print("   - show_current_status(): Show current stats")
print()
print("🎯 To start demo, run: run_log_analysis_demo()")
print("🔍 For quick test, run: quick_error_analysis('my-app', 'Connection failed')")


# Run full demo with sample logs
run_log_analysis_demo()

# Analyze a single error quickly
quick_error_analysis('payment-service', 'Database connection timeout')

# Check current status
show_current_status()

# Analyze custom log
analyze_custom_log('my-app', 'ERROR', 'Redis connection failed', 'user_456')

# Create and analyze your own logs
my_logs = [
    create_sample_log('web-server', 'ERROR', 'Memory leak detected'),
    create_sample_log('database', 'CRITICAL', 'Disk space at 98%')
]
batch_analyze_logs(my_logs, delay_seconds=1)