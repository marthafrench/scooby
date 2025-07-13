#!/usr/bin/env python3
"""
🐕 Simple Scooby AI - Log Analysis with LangChain + TinyLlama
Analyzes logs every minute and provides fix recommendations
"""

import json
import time
import threading
import os
from datetime import datetime
from collections import deque

# LangChain imports for local TinyLlama
try:
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage

    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("❌ Install: pip install langchain langchain-community")
    LANGCHAIN_AVAILABLE = False


# ============================================================================
# SIMPLE SCOOBY ANALYZER WITH LANGCHAIN + TINYLLAMA
# ============================================================================

class SimpleScoobyAnalyzer:
    """Simple log analyzer using LangChain + TinyLlama (local)"""

    def __init__(self, model_name="tinyllama"):
        self.model_name = model_name
        self.recent_logs = deque(maxlen=100)  # Keep last 100 logs in memory
        self.error_logs = deque(maxlen=20)  # Keep last 20 errors for analysis

        if LANGCHAIN_AVAILABLE:
            try:
                # Initialize LangChain with TinyLlama via Ollama
                self.llm = Ollama(
                    model=self.model_name,
                    temperature=0.1,
                    num_predict=200  # Limit response length for TinyLlama
                )

                # Test if TinyLlama is available
                test_response = self.llm.invoke("Hello")

                # Create simpler prompt template for TinyLlama
                self.prompt_template = PromptTemplate(
                    input_variables=["application", "level", "message"],
                    template="""You are a system administrator. Fix this error:

Application: {application}
Error Level: {level}
Error Message: {message}

Give 3 short fixes:
1. 
2. 
3. """
                )

                print("✅ LangChain + TinyLlama initialized")

            except Exception as e:
                print(f"❌ TinyLlama connection failed: {e}")
                print("💡 Make sure Ollama is running with TinyLlama:")
                print("   ollama run tinyllama")
                self.llm = None
        else:
            print("❌ LangChain not available")
            self.llm = None

    def analyze_log(self, log):
        """Analyze each incoming log"""
        # Store in memory
        self.recent_logs.append(log)

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 📥 [{log['level']}] {log['application']}: {log['message']}")

        # If it's an error, analyze it with AI
        if log['level'] in ['ERROR', 'CRITICAL']:
            self.error_logs.append(log)
            print(f"🚨 Error detected! Analyzing with TinyLlama...")

            # Get AI recommendations
            recommendations = self.get_ai_recommendations(log)

            print(f"\n🤖 AI ANALYSIS (TinyLlama):")
            print(f"📱 Application: {log['application']}")
            print(f"🔍 Issue: {log['message']}")
            print(f"💡 Fix Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
            print("=" * 60)

    def get_ai_recommendations(self, error_log):
        """Get fix recommendations using LangChain + TinyLlama"""
        if not LANGCHAIN_AVAILABLE or not self.llm:
            return ["AI analysis not available - check TinyLlama setup"]

        try:
            # Format the prompt (simpler for TinyLlama)
            prompt = self.prompt_template.format(
                application=error_log['application'],
                level=error_log['level'],
                message=error_log['message']
            )

            # Get response from TinyLlama via LangChain
            response = self.llm.invoke(prompt)

            # Parse recommendations
            recommendations = self._parse_recommendations(response)
            return recommendations

        except Exception as e:
            print(f"❌ LangChain/TinyLlama analysis failed: {e}")
            return [f"AI analysis failed: {e}"]

    def _parse_recommendations(self, response_text):
        """Parse recommendations from TinyLlama response"""
        try:
            lines = response_text.strip().split('\n')
            recommendations = []

            for line in lines:
                line = line.strip()
                # Look for numbered recommendations
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    # Remove numbering and clean up
                    rec = line.split('.', 1)[-1].strip()
                    if rec and len(rec) > 3:  # Must be substantial
                        recommendations.append(rec)
                elif line and len(line) > 10 and not any(x in line.lower() for x in ['error', 'application', 'level']):
                    # Catch recommendations that aren't numbered
                    recommendations.append(line)

            # Fallback parsing for TinyLlama's varied responses
            if not recommendations:
                # Split by common delimiters and filter
                parts = response_text.replace('\n', ' ').split('.')
                for part in parts:
                    part = part.strip()
                    if len(part) > 15 and len(part) < 100:  # Reasonable length
                        recommendations.append(part)

            # Final fallback
            if not recommendations:
                recommendations = [response_text.strip()[:100]]  # Truncate if too long

            return recommendations[:3]  # Max 3 recommendations

        except Exception as e:
            return [f"Could not parse AI response: {e}"]

    def get_status(self):
        """Get analyzer status"""
        return {
            'total_logs_analyzed': len(self.recent_logs),
            'error_logs_found': len(self.error_logs),
            'tinyllama_available': LANGCHAIN_AVAILABLE and bool(self.llm),
            'recent_errors': len([log for log in self.recent_logs if log['level'] in ['ERROR', 'CRITICAL']])
        }


# ============================================================================
# SIMPLE LOG PUSHER
# ============================================================================

def push_logs_from_json_simple(json_file_path, callback=None, interval_seconds=60):
    """Push logs from JSON file every interval_seconds"""

    try:
        with open(json_file_path, 'r') as f:
            logs = json.load(f)
        print(f"✅ Loaded {len(logs)} logs from {json_file_path}")
    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON error: {e}")
        return None

    if not logs:
        return None

    state = {'current_index': 0, 'running': True, 'logs': logs}

    def push_loop():
        print(f"🚀 Starting to push {len(logs)} logs, one every {interval_seconds} seconds")

        while state['running'] and state['current_index'] < len(logs):
            # Get current log and update timestamp
            current_log = logs[state['current_index']].copy()
            current_log['timestamp'] = datetime.utcnow().isoformat() + 'Z'

            # Send to callback (analyzer)
            if callback:
                callback(current_log)

            state['current_index'] += 1

            # Check if done
            if state['current_index'] >= len(logs):
                print(f"✅ Finished pushing all {len(logs)} logs!")
                state['running'] = False
                break

            # Wait for next interval
            if state['running']:
                time.sleep(interval_seconds)

    # Start background thread
    thread = threading.Thread(target=push_loop, daemon=False)
    thread.start()

    # Return simple control object
    class PusherControl:
        def stop(self):
            state['running'] = False
            print("🛑 Log pushing stopped")

        def status(self):
            return {
                'total_logs': len(logs),
                'logs_pushed': state['current_index'],
                'logs_remaining': len(logs) - state['current_index'],
                'running': state['running']
            }

    return PusherControl()


# ============================================================================
# SAMPLE DATA CREATOR
# ============================================================================

def create_sample_logs(filename='sample_logs.json', num_logs=10):
    """Create sample logs with realistic error patterns"""

    applications = ['payment-gateway', 'user-auth', 'notification-service', 'api-gateway']

    sample_logs = []
    for i in range(num_logs):
        app = applications[i % len(applications)]

        # Create realistic error patterns
        if i % 4 == 0:  # Every 4th log is an error
            if app == 'payment-gateway':
                log = {
                    'timestamp': '2024-07-10T14:30:00.000Z',
                    'level': 'ERROR',
                    'application': app,
                    'user_id': f'user_{1000 + i}',
                    'correlation_id': f'req_payment_{i:03d}',
                    'message': f'Database connection timeout after 30 seconds',
                    'stack_trace': 'java.sql.SQLTimeoutException: Connection timeout'
                }
            elif app == 'user-auth':
                log = {
                    'timestamp': '2024-07-10T14:30:00.000Z',
                    'level': 'ERROR',
                    'application': app,
                    'user_id': f'user_{1000 + i}',
                    'correlation_id': f'req_auth_{i:03d}',
                    'message': f'JWT token validation failed - Redis unavailable',
                    'stack_trace': 'redis.exceptions.ConnectionError: Redis connection failed'
                }
            else:
                log = {
                    'timestamp': '2024-07-10T14:30:00.000Z',
                    'level': 'ERROR',
                    'application': app,
                    'user_id': f'user_{1000 + i}',
                    'correlation_id': f'req_{app}_{i:03d}',
                    'message': f'Service unavailable - downstream failure',
                    'stack_trace': f'java.net.ConnectException: Connection refused'
                }

        elif i % 7 == 0:  # Some critical errors
            log = {
                'timestamp': '2024-07-10T14:30:00.000Z',
                'level': 'CRITICAL',
                'application': app,
                'user_id': f'user_{1000 + i}',
                'correlation_id': f'req_{app}_{i:03d}',
                'message': f'{app} service completely down',
                'stack_trace': f'System.Exception: Critical service failure'
            }

        else:  # Normal logs
            log = {
                'timestamp': '2024-07-10T14:30:00.000Z',
                'level': 'INFO',
                'application': app,
                'user_id': f'user_{1000 + i}',
                'correlation_id': f'req_{app}_{i:03d}',
                'message': f'Request processed successfully',
                'stack_trace': None
            }

        sample_logs.append(log)

    # Save to file
    with open(filename, 'w') as f:
        json.dump(sample_logs, f, indent=2)

    print(f"📁 Created {filename} with {num_logs} logs")
    return filename


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function - Simple Scooby AI with TinyLlama"""
    print("🐕 Simple Scooby AI - LangChain + TinyLlama (Local)")
    print("=" * 60)

    # Check if Ollama is running
    print("💡 Make sure Ollama is running with TinyLlama:")
    print("   1. Install Ollama: https://ollama.ai")
    print("   2. Run: ollama run tinyllama")
    print("   3. Wait for download to complete")
    print()

    # Initialize analyzer
    analyzer = SimpleScoobyAnalyzer("tinyllama")

    # Create sample data if needed
    log_file = 'scooby_logs.json'
    if not os.path.exists(log_file):
        print(f"📁 Creating sample log file: {log_file}")
        create_sample_logs(log_file, num_logs=8)

    # Start log analysis
    print(f"\n🚀 Starting log analysis...")
    print(f"📊 Logs will be analyzed every 60 seconds")
    print(f"🤖 Errors will get AI recommendations from TinyLlama")
    print(f"🛑 Press Ctrl+C to stop\n")

    # Start pushing logs to analyzer
    pusher = push_logs_from_json_simple(
        log_file,
        callback=analyzer.analyze_log,  # Send each log to analyzer
        interval_seconds=60  # 1 log per minute
    )

    if not pusher:
        print("❌ Failed to start log pusher")
        return

    try:
        # Let it run and show periodic status
        while pusher.status()['running']:
            time.sleep(30)  # Check every 30 seconds

            status = analyzer.get_status()
            pusher_status = pusher.status()

            print(f"\n📊 STATUS UPDATE:")
            print(f"   Logs analyzed: {status['total_logs_analyzed']}")
            print(f"   Errors found: {status['error_logs_found']}")
            print(f"   Progress: {pusher_status['logs_pushed']}/{pusher_status['total_logs']}")
            print(f"   TinyLlama ready: {status['tinyllama_available']}")

        print("\n✅ All logs processed!")

    except KeyboardInterrupt:
        print("\n🛑 Stopping Scooby...")
        pusher.stop()

    # Final status
    final_status = analyzer.get_status()
    print(f"\n📊 FINAL STATS:")
    print(f"   Total logs analyzed: {final_status['total_logs_analyzed']}")
    print(f"   Total errors found: {final_status['error_logs_found']}")
    print(f"   Recent errors: {final_status['recent_errors']}")


if __name__ == "__main__":
    main()
