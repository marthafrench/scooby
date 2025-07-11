#!/usr/bin/env python3
"""
Simple Log Pusher - Just one function that does exactly what you asked for
"""

import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional

# Global variable to control the pusher
_current_pusher = None


def push_logs_from_json_simple(json_file_path: str, callback: Optional[Callable] = None, interval_seconds: int = 60):
    """
    Simple function that pushes one log per minute from JSON file until empty
    Runs in background thread so it doesn't block

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
        print(f"✅ Loaded {len(logs)} logs from {json_file_path}")
    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON error: {e}")
        return None

    if not logs:
        print("❌ No logs found in file")
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
        print(f"🚀 Starting to push {len(logs)} logs, one every {interval_seconds} seconds")

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
                print(f"\n[{timestamp}] 📤 Log {state['current_index'] + 1}/{len(logs)}")
                print(f"   App: {current_log['application']}")
                print(f"   Level: {current_log['level']}")
                print(f"   Message: {current_log['message']}")
                print(f"   📊 {len(logs) - state['current_index'] - 1} logs remaining")

            state['current_index'] += 1

            # Check if done
            if state['current_index'] >= len(logs):
                print(f"✅ Finished pushing all {len(logs)} logs!")
                state['running'] = False
                break

            # Wait for next interval
            if state['running']:
                time.sleep(interval_seconds)

    # Start background thread (not daemon so it can complete)
    state['thread'] = threading.Thread(target=push_loop, daemon=False)
    state['thread'].start()

    # Create control object that works like an object with methods
    class PusherControl:
        def __init__(self, state):
            self._state = state

        def stop(self):
            self._state['running'] = False
            print("🛑 Log pushing stopped")

        def status(self):
            return {
                'total_logs': len(logs),
                'logs_pushed': self._state['current_index'],
                'logs_remaining': len(logs) - self._state['current_index'],
                'running': self._state['running'],
                'progress_percent': round((self._state['current_index'] / len(logs)) * 100, 1)
            }

        def logs_remaining(self):
            return len(logs) - self._state['current_index']

        def wait_for_completion(self, check_interval: int = 10):
            """
            Wait for all logs to be pushed (blocking)

            Args:
                check_interval: Seconds between status checks
            """
            print(f"⏳ Waiting for all {len(logs)} logs to complete...")
            while self._state['running'] and self._state['current_index'] < len(logs):
                time.sleep(check_interval)
                remaining = len(logs) - self._state['current_index']
                if remaining > 0:
                    print(f"📊 Status: {self._state['current_index']}/{len(logs)} complete, {remaining} remaining")

            if self._state['current_index'] >= len(logs):
                print("✅ All logs completed!")
            else:
                print("🛑 Stopped before completion")

        @property
        def running(self):
            return self._state['running']

    control = PusherControl(state)
    _current_pusher = control
    return control


# Helper function for easy testing
def quick_test_pusher(interval_seconds: int = 3, num_logs: int = 3):
    """
    Quick test function - creates sample data and starts pusher

    Args:
        interval_seconds: Seconds between logs (default: 5 for quick testing)
        num_logs: Number of logs to create (default: 3)

    Returns:
        PusherControl object
    """
    print(f"🎯 Quick Test: Creating {num_logs} logs, pushing every {interval_seconds} seconds")

    # Create small test file
    test_logs = []
    apps = ['payment-gateway', 'user-auth', 'notification-service']
    levels = ['INFO', 'WARN', 'ERROR']

    for i in range(num_logs):
        test_logs.append({
            'timestamp': '2024-07-10T14:30:00.000Z',
            'level': levels[i % len(levels)],
            'application': apps[i % len(apps)],
            'user_id': f'user_test_{i + 1}',
            'correlation_id': f'req_test_{i + 1:03d}',
            'message': f'Test message {i + 1} - {levels[i % len(levels)]} from {apps[i % len(apps)]}',
            'stack_trace': 'java.lang.Exception: Test stack trace' if levels[i % len(levels)] == 'ERROR' else None
        })

    # Save test file
    with open('quick_test.json', 'w') as f:
        json.dump(test_logs, f, indent=2)

    # Start pusher
    pusher = push_logs_from_json_simple('quick_test.json', interval_seconds=interval_seconds)

    if pusher:
        print(f"✅ Test pusher started! Will complete in ~{num_logs * interval_seconds} seconds")
        print(f"   Use pusher.status() to check progress")
        print(f"   Use pusher.stop() to stop early")

    return pusher


def stop_current_pusher():
    """Stop any currently running pusher"""
    global _current_pusher
    if _current_pusher and _current_pusher.running:
        _current_pusher.stop()
        _current_pusher = None
        print("🛑 Stopped current pusher")


# Example usage functions
def create_sample_json(filename: str = 'sample_logs.json'):
    """Create a sample JSON file for testing"""
    sample_logs = [
        {
            'timestamp': '2024-07-10T14:24:15.789Z',
            'level': 'INFO',
            'application': 'notification-service',
            'user_id': 'user_77777',
            'correlation_id': 'req_notif345jkl678',
            'message': 'Email notification sent successfully',
            'stack_trace': None
        },
        {
            'timestamp': '2024-07-10T14:30:45.567Z',
            'level': 'ERROR',
            'application': 'notification-service',
            'user_id': 'user_88888',
            'correlation_id': 'req_notif678mno901',
            'message': 'Email delivery failed for batch_id: 789 - SMTP server error',
            'stack_trace': '''javax.mail.SendFailedException: Invalid Addresses
    at com.notification.email.EmailSender.sendBatch(EmailSender.java:178)
    at com.notification.service.BatchEmailService.process(BatchEmailService.java:234)'''
        },
        {
            'timestamp': '2024-07-10T14:32:10.123Z',
            'level': 'ERROR',
            'application': 'payment-gateway',
            'user_id': 'user_12345',
            'correlation_id': 'req_payment123abc',
            'message': 'Database connection timeout after 30 seconds',
            'stack_trace': '''java.sql.SQLTimeoutException: Connection timeout
    at com.payment.db.ConnectionPool.getConnection(ConnectionPool.java:156)
    at com.payment.service.PaymentService.processPayment(PaymentService.java:89)'''
        },
        {
            'timestamp': '2024-07-10T14:34:15.456Z',
            'level': 'CRITICAL',
            'application': 'payment-gateway',
            'user_id': 'user_99999',
            'correlation_id': 'req_payment456def',
            'message': 'Payment processing completely unavailable',
            'stack_trace': '''java.sql.SQLException: Cannot create PoolableConnectionFactory
    at com.payment.db.ConnectionManager.initializePool(ConnectionManager.java:234)
    at com.payment.service.DatabaseService.connect(DatabaseService.java:78)'''
        },
        {
            'timestamp': '2024-07-10T14:36:30.789Z',
            'level': 'INFO',
            'application': 'user-auth',
            'user_id': 'user_11111',
            'correlation_id': 'req_auth789ghi',
            'message': 'User authentication successful',
            'stack_trace': None
        }
    ]

    with open(filename, 'w') as f:
        json.dump(sample_logs, f, indent=2)

    print(f"📁 Created {filename} with {len(sample_logs)} sample logs")
    return filename


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("🐕 Simple Log Pusher Function")
    print("=" * 40)

    # Create sample data first
    sample_file = create_sample_json('demo_logs.json')

    print("\n🎯 EXAMPLE: Basic usage (1 log per minute)")
    print("This will push 5 logs, one every 60 seconds in the background:")
    print("NOTE: Pusher will continue running until all logs are complete")

    # Push logs every 60 seconds (1 per minute)
    pusher = push_logs_from_json_simple('demo_logs.json', interval_seconds=60)

    if pusher is None:
        print("❌ Failed to create pusher")
    else:
        print("✅ Pusher started! Logs will appear every minute until complete.")
        print("📊 Check status anytime with: pusher.status()")
        print("🛑 Stop early with: pusher.stop()")
        print("\n" + "=" * 50)
        print("PUSHER IS NOW RUNNING IN BACKGROUND")
        print("The program will continue, but logs will keep appearing every 60 seconds")
        print("until all 5 logs are pushed (about 5 minutes total)")
        print("=" * 50)

        # Just show that it started, don't wait
        print(f"\n⏰ Pusher running... {pusher.logs_remaining()} logs remaining")
        print("💡 Tip: Use pusher.stop() to stop early, or let it complete naturally")