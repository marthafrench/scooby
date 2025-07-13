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