# Cell 6: Main Analysis Function
"""
Cell 6: Main Log Analysis and Recommendation Engine
"""


def analyze_error_with_ai(error_log):
    """
    Analyze error log using AI and generate recommendations

    Args:
        error_log: Dictionary containing error log data

    Returns:
        Dictionary with analysis results
    """
    if analysis_chain is None:
        return {
            'success': False,
            'error': 'Analysis chain not available',
            'root_cause': 'AI analysis unavailable',
            'recommendations': ['Check AI model setup']
        }

    try:
        print(f"🤖 Analyzing error with Gemini 2.0 Flash...")

        # Prepare context from recent logs
        context_logs = format_context_logs(list(recent_logs), max_logs=5)

        # Prepare input for AI chain
        analysis_input = {
            'application': error_log.get('application', 'unknown'),
            'level': error_log.get('level', 'ERROR'),
            'message': error_log.get('message', 'No message available'),
            'user_id': error_log.get('user_id', 'unknown'),
            'correlation_id': error_log.get('correlation_id', 'unknown'),
            'context_logs': context_logs,
            'timestamp': error_log.get('timestamp', datetime.now().isoformat())
        }

        # Get AI analysis
        ai_response = analysis_chain.run(analysis_input)

        # Parse the response
        parsed_analysis = parse_ai_response(ai_response)

        # Create analysis result
        analysis_result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'incident_id': f"INC-{error_log['application']}-{int(time.time())}",
            'error_log': error_log,
            'root_cause': parsed_analysis['root_cause'],
            'recommendations': parsed_analysis['recommendations'],
            'raw_ai_response': ai_response,
            'confidence_score': len(parsed_analysis['recommendations']) * 30  # Simple confidence metric
        }

        # Store in analysis history
        analysis_history.append(analysis_result)

        print("✅ AI analysis completed")
        return analysis_result

    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'root_cause': f'Analysis failed: {e}',
            'recommendations': ['Manual investigation required due to AI failure']
        }


def process_and_analyze_log(log_data):
    """
    Complete workflow: process log and analyze if error

    Args:
        log_data: Dictionary containing log information

    Returns:
        Analysis result if error, None if normal log
    """
    # Process the log entry
    processed = process_log_entry(log_data)

    if not processed:
        return None

    # If it's an error, analyze it
    if log_data['level'] in ['ERROR', 'CRITICAL']:
        analysis_result = analyze_error_with_ai(log_data)

        if analysis_result['success']:
            print(f"\n🎯 INCIDENT ANALYSIS:")
            print(f"📱 Application: {log_data['application']}")
            print(f"🆔 Incident ID: {analysis_result['incident_id']}")
            print(f"🔍 Root Cause: {analysis_result['root_cause']}")
            print(f"💡 Fix Recommendations:")

            for i, rec in enumerate(analysis_result['recommendations'], 1):
                print(f"   {i}. {rec}")

            print(f"📊 Confidence: {analysis_result['confidence_score']}%")
            print("=" * 70)

        return analysis_result

    return None


def analyze_logs_from_file(filename, interval_seconds=60):
    """
    Load logs from JSON file and analyze them with specified interval

    Args:
        filename: Path to JSON file containing logs
        interval_seconds: Seconds between processing each log
    """
    try:
        with open(filename, 'r') as f:
            logs = json.load(f)

        print(f"✅ Loaded {len(logs)} logs from {filename}")
        print(f"🕐 Processing interval: {interval_seconds} seconds")
        print("🛑 Press Ctrl+C to stop\n")

        incident_count = 0

        for i, log in enumerate(logs, 1):
            print(f"\n📋 Processing log {i}/{len(logs)}:")

            # Update timestamp to current time
            log['timestamp'] = datetime.utcnow().isoformat() + 'Z'

            # Process and analyze
            analysis = process_and_analyze_log(log)

            if analysis and analysis['success']:
                incident_count += 1

            # Wait before next log (except for last one)
            if i < len(logs):
                print(f"⏳ Waiting {interval_seconds} seconds for next log...")
                time.sleep(interval_seconds)

        # Final summary
        stats = get_log_statistics()
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Total logs processed: {stats['total_logs_processed']}")
        print(f"   Incidents analyzed: {incident_count}")
        print(f"   Error logs stored: {stats['total_errors_stored']}")
        print(f"   Applications seen: {list(stats['applications'].keys())}")

        return stats

    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None
    except KeyboardInterrupt:
        print("\n🛑 Analysis stopped by user")
        return get_log_statistics()


def create_sample_logs(filename='sample_logs.json', num_logs=5):
    """Create sample logs for testing"""
    applications = ['payment-gateway', 'user-auth', 'notification-service']

    sample_logs = []
    for i in range(num_logs):
        app = applications[i % len(applications)]

        if i % 3 == 0:  # Every 3rd log is an error
            level = 'ERROR' if i % 6 != 0 else 'CRITICAL'
            if app == 'payment-gateway':
                message = 'Database connection timeout after 30 seconds'
            elif app == 'user-auth':
                message = 'JWT token validation failed - Redis unavailable'
            else:
                message = 'Email delivery service unreachable'
        else:
            level = 'INFO'
            message = 'Request processed successfully'

        log = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'application': app,
            'user_id': f'user_{1000 + i}',
            'correlation_id': f'req_{app}_{i:03d}',
            'message': message
        }
        sample_logs.append(log)

    with open(filename, 'w') as f:
        json.dump(sample_logs, f, indent=2)

    print(f"📁 Created {filename} with {num_logs} logs")
    return filename


# Main functions available
print("✅ Main analysis functions ready:")
print("   - analyze_error_with_ai(error_log)")
print("   - process_and_analyze_log(log_data)")
print("   - analyze_logs_from_file(filename, interval_seconds=60)")
print("   - create_sample_logs(filename, num_logs=5)")

print("\n🚀 Ready to analyze logs!")
print("📋 Example usage:")
print("   # Create sample data")
print("   create_sample_logs('test_logs.json', 8)")
print()
print("   # Analyze logs from file (every 10 seconds for testing)")
print("   analyze_logs_from_file('test_logs.json', interval_seconds=10)")
print()
print("   # Or analyze single log")
print("   error_log = {'level': 'ERROR', 'application': 'test', 'message': 'Test error'}")
print("   process_and_analyze_log(error_log)")