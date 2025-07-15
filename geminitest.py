# Final demonstration with actual log parsing
sample_log = "2025-01-15 16:45:12 CRITICAL [payment-service] Payment gateway timeout: external API unreachable after 30s retry_count=3 transaction_id=txn_999888"
sample_entry = LogEntry(sample_log, source="demo", service="payment-service")

# Set your API key
import os
os.environ['GEMINI_API_KEY'] = 'your-actual-api-key-here'

# Reinitialize
config = ScoobyConfig()
gemini_analyzer = GeminiAnalyzer(config)
scooby_agent = ScoobyAgent(tools, gemini_analyzer)

# Analyze real logs
result = await scooby_agent.analyze_incident('''
2025-01-15 14:30:22 ERROR [webapp] HTTP 500 Database timeout
2025-01-15 14:30:25 CRITICAL [database] Connection lost
''', {{# Scooby: AI-Powered System Log Analyzer
# Using LangChain Agents with Gemini 2.0 Flash for Intelligent Incident Response

## Overview
This notebook implements an AI-powered incident response system that:
- Analyzes system logs using Gemini 2.0 Flash
- Provides intelligent insights and resolution guidance
- Uses LangChain agents for structured analysis workflows
- Integrates with existing log sources (Splunk simulation)

import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

# Core LangChain imports
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.tools import tool

# Gemini integration (simulated for demo - replace with actual Google AI SDK)
# pip install google-generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Google Generative AI SDK loaded successfully")
except ImportError:
    print("❌ Google Generative AI not installed. Install with: pip install google-generativeai")
    GEMINI_AVAILABLE = False

# For demo purposes - sample log data
import warnings
warnings.filterwarnings('ignore')

print("🔧 Scooby System Log Analyzer Initialized")
print("📊 Ready for intelligent incident response!")

## 1. Configuration and Setup

class ScoobyConfig:
    """
Configuration
management
for Scooby system"""

    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = 'gemini-2.0-flash-exp'
        self.splunk_host = os.getenv('SPLUNK_HOST', 'localhost:8089')
        self.confidence_threshold = 0.7
        self.max_retries = 3

        # Rate limiting configuration
        self.rate_limits = {
            'free': {'rpm': 15, 'tpm': 1000000},
            'paid_tier_1': {'rpm': 2000, 'tpm': 4000000},
            'paid_tier_2': {'rpm': 10000, 'tpm': 10000000}
        }

        # Initialize Gemini - REQUIRES VALID API KEY
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel(self.gemini_model)
                print(f"✅ Gemini 2.0 Flash initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
                self.model = None
        else:
            self.model = None
            if not self.gemini_api_key:
                print("❌ GEMINI_API_KEY environment variable not set!")
                print("   Set it with: os.environ['GEMINI_API_KEY'] = 'your-actual-api-key'")

    def get_tier_info(self, tier: str) -> Dict:
        """Get rate limiting information for specified tier"""
        return self.rate_limits.get(tier, self.rate_limits['free'])

config = ScoobyConfig()
print(f"✅ Configuration loaded - Model: {config.gemini_model}")

## 2. Enhanced Log Data Models

class LogEntry:
    """Structured log entry with metadata"""

    def __init__(self, raw_log: str, source: str = "unknown", service: str = "unknown"):
        self.raw_log = raw_log
        self.source = source
        self.service = service
        self.timestamp = self._extract_timestamp()
        self.severity = self._extract_severity()
        self.error_code = self._extract_error_code()
        self.hash = self._generate_hash()
        self.structured_data = self._parse_structured_data()

    def _extract_timestamp(self) -> Optional[datetime]:
        """Extract timestamp from log entry"""
        patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\w{3} \d{2} \d{2}:\d{2}:\d{2}'
        ]

        for pattern in patterns:
            match = re.search(pattern, self.raw_log)
            if match:
                try:
                    return datetime.fromisoformat(match.group().replace('T', ' '))
                except:
                    pass
        return datetime.now()

    def _extract_severity(self) -> str:
        """Extract severity level from log"""
        severity_patterns = {
            'CRITICAL': r'\b(CRITICAL|FATAL|EMERGENCY)\b',
            'ERROR': r'\b(ERROR|ERR)\b',
            'WARNING': r'\b(WARNING|WARN)\b',
            'INFO': r'\b(INFO|INFORMATION)\b',
            'DEBUG': r'\b(DEBUG|TRACE)\b'
        }

        for severity, pattern in severity_patterns.items():
            if re.search(pattern, self.raw_log, re.IGNORECASE):
                return severity
        return 'UNKNOWN'

    def _extract_error_code(self) -> Optional[str]:
        """Extract error codes from log"""
        patterns = [
            r'HTTP[/\s]?\d{3}',
            r'Error[:\s]*(\d+)',
            r'Code[:\s]*(\d+)',
            r'\b5\d{2}\b',  # 5xx errors
            r'\b4\d{2}\b'   # 4xx errors
        ]

        for pattern in patterns:
            match = re.search(pattern, self.raw_log, re.IGNORECASE)
            if match:
                return match.group()
        return None

    def _generate_hash(self) -> str:
        """Generate hash for caching similar logs"""
        # Normalize log for hashing (remove timestamps, IPs, etc.)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', 'TIMESTAMP', self.raw_log)
        normalized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP_ADDRESS', normalized)
        normalized = re.sub(r'\b[a-f0-9-]{36}\b', 'UUID', normalized)

        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _parse_structured_data(self) -> Dict:
        """Parse structured data from logs"""
        data = {}

        # Extract key-value pairs
        kv_pattern = r'(\w+)=(["\']?)([^"\'\s,]+)\2'
        matches = re.findall(kv_pattern, self.raw_log)

        for key, _, value in matches:
            data[key.lower()] = value

        return data

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'raw_log': self.raw_log,
            'source': self.source,
            'service': self.service,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'severity': self.severity,
            'error_code': self.error_code,
            'hash': self.hash,
            'structured_data': self.structured_data
        }

# Sample log data for demonstration
SAMPLE_LOGS = [
    "2025-01-15 14:30:22 ERROR [webapp] HTTP 500 Internal Server Error: Database connection timeout after 30s user_id=12345 session=abc-def-123",
    "2025-01-15 14:30:25 CRITICAL [database] MySQL server has gone away. Connection lost during transaction. Table: user_sessions, Query: SELECT * FROM user_sessions WHERE session_id='abc-def-123'",
    "2025-01-15 14:30:30 WARNING [loadbalancer] Health check failed for backend server 192.168.1.100:8080. Removing from pool.",
    "2025-01-15 14:31:45 INFO [webapp] Auto-retry successful. Database connection restored. user_id=12345",
    "2025-01-15 14:32:12 ERROR [auth-service] JWT token validation failed: token expired. user_id=67890 endpoint=/api/secure/data",
    "2025-01-15 14:33:01 CRITICAL [payment-gateway] Payment processing failed: Gateway timeout. transaction_id=txn_98765 amount=299.99"
]

print("🔍 Log parsing models initialized")

## 3. Gemini 2.0 Flash Integration

class GeminiAnalyzer:
    """Gemini 2.0 Flash integration for log analysis"""

    def __init__(self, config: ScoobyConfig):
        self.config = config
        self.model = config.model
        self.response_cache = {}  # Simple in-memory cache

    def _generate_analysis_prompt(self, logs: List[LogEntry], context: Dict = None) -> str:
        """Generate analysis prompt for Gemini"""

        prompt = """You are an expert Site Reliability Engineer (SRE) analyzing system logs for incident response.

** Your Task **: Analyze
the
provided
logs and provide
structured
incident
response
guidance.

** Analysis
Framework **:
1. ** Incident
Classification **: Severity(P0 - P3), Category, Impact
Assessment
2. ** Root
Cause
Analysis **: Primary
cause, Contributing
factors, Evidence
from logs

3. ** Resolution
Guidance **: Immediate
actions, Step - by - step
remediation, Preventive
measures
4. ** Confidence
Assessment **: Your
confidence
level(0 - 100 %) and reasoning

** Context
Information **:
"""

        if context:
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"

        prompt += f"""
** System
Logs
to
Analyze **:
{'-' * 50}
"""

        for i, log in enumerate(logs, 1):
            prompt += f"""
Log
{i}:
- Timestamp: {log.timestamp}
             - Severity: {log.severity}
                         - Service: {log.service}
                                    - Error
Code: {log.error_code}
      - Content: {log.raw_log}
"""

        prompt += f"""
{'-' * 50}

** Required
Response
Format **:
```json
{{
    "incident_classification": {{
        "severity": "P0|P1|P2|P3",
        "category": "string",
        "impact_assessment": "string",
        "affected_services": ["service1", "service2"]
    }},
    "root_cause_analysis": {{
        "primary_cause": "string",
        "contributing_factors": ["factor1", "factor2"],
        "evidence_summary": "string",
        "log_citations": [1, 2, 3]
    }},
    "resolution_guidance": {{
        "immediate_actions": ["action1", "action2"],
        "step_by_step_remediation": [
            {{"step": 1, "action": "string", "expected_outcome": "string"}},
            {{"step": 2, "action": "string", "expected_outcome": "string"}}
        ],
        "preventive_measures": ["measure1", "measure2"]
    }},
    "confidence_assessment": {{
        "overall_confidence": 85,
        "reasoning": "string",
        "areas_of_uncertainty": ["area1", "area2"]
    }},
    "escalation_criteria": {{
        "escalate_if": ["condition1", "condition2"],
        "suggested_contacts": ["team1", "team2"]
    }}
}}
```

  ** Important
Guidelines **:
- Cite
specific
log
entries
by
number
when
providing
evidence
- Focus
on
actionable
recommendations
- Consider
service
dependencies and cascading
failures
- Provide
realistic
timelines
for resolution steps
               - Be honest about confidence levels and uncertainties
"""
        return prompt

    async def analyze_logs(self, logs: List[LogEntry], context: Dict = None) -> Dict:
        """Analyze logs using Gemini 2.0 Flash"""

        if not self.model:
            raise Exception("Gemini 2.0 Flash not available. Please set GEMINI_API_KEY environment variable.")

        # Generate cache key
        log_hashes = [log.hash for log in logs]
        context_str = json.dumps(context or {}, sort_keys=True)
        cache_key = hashlib.md5((str(sorted(log_hashes)) + context_str).encode()).hexdigest()

        # Check cache first
        if cache_key in self.response_cache:
            print("📋 Using cached analysis result")
            return self.response_cache[cache_key]

        # Generate prompt
        prompt = self._generate_analysis_prompt(logs, context)

        try:
            print("🤖 Sending analysis request to Gemini 2.0 Flash...")

            # Real Gemini API call
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent analysis
                    top_p=0.8,
                    max_output_tokens=2048,
                )
            )

            print("✅ Received response from Gemini")

            # Parse JSON response
            response_text = response.text

            # Extract JSON from response (Gemini sometimes wraps JSON in markdown)
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(1))
            else:
                # Try to find JSON object in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    analysis = json.loads(response_text[json_start:json_end])
                else:
                    raise ValueError("No valid JSON found in Gemini response")

            # Validate required fields
            required_fields = ['incident_classification', 'root_cause_analysis', 'resolution_guidance', 'confidence_assessment']
            for field in required_fields:
                if field not in analysis:
                    print(f"⚠️  Warning: Missing required field '{field}' in Gemini response")

            # Cache the result
            self.response_cache[cache_key] = analysis
            print(f"💾 Analysis cached with key: {cache_key[:8]}...")

            return analysis

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON from Gemini response: {e}")
            print(f"Raw response: {response_text[:500]}...")
            raise Exception(f"Invalid JSON response from Gemini: {e}")

        except Exception as e:
            print(f"❌ Error during Gemini analysis: {str(e)}")
            raise Exception(f"Gemini analysis failed: {e}")

    def _generate_mock_analysis(self, logs: List[LogEntry]) -> Dict:
        """Generate mock analysis for demo purposes"""

        # Determine severity based on log content
        has_critical = any(log.severity == 'CRITICAL' for log in logs)
        has_error = any(log.severity == 'ERROR' for log in logs)

        if has_critical:
            severity = "P1"
        elif has_error:
            severity = "P2"
        else:
            severity = "P3"

        services = list(set(log.service for log in logs if log.service != "unknown"))

        return {
            "incident_classification": {
                "severity": severity,
                "category": "Service Degradation",
                "impact_assessment": f"Multiple services affected: {', '.join(services)}",
                "affected_services": services
            },
            "root_cause_analysis": {
                "primary_cause": "Database connectivity issues leading to cascading failures",
                "contributing_factors": [
                    "Database connection timeout",
                    "Insufficient connection pool size",
                    "Missing circuit breaker protection"
                ],
                "evidence_summary": "Database connection timeouts observed, followed by downstream service failures",
                "log_citations": [1, 2]
            },
            "resolution_guidance": {
                "immediate_actions": [
                    "Check database server status and connectivity",
                    "Scale up database connection pool",
                    "Enable circuit breaker for database calls"
                ],
                "step_by_step_remediation": [
                    {
                        "step": 1,
                        "action": "Verify database server health and connectivity",
                        "expected_outcome": "Confirm database is operational and reachable"
                    },
                    {
                        "step": 2,
                        "action": "Increase database connection pool size temporarily",
                        "expected_outcome": "Reduce connection timeouts"
                    },
                    {
                        "step": 3,
                        "action": "Restart affected application services",
                        "expected_outcome": "Clear stale connections and restore service"
                    }
                ],
                "preventive_measures": [
                    "Implement database connection monitoring",
                    "Set up circuit breakers for external dependencies",
                    "Review and optimize slow database queries"
                ]
            },
            "confidence_assessment": {
                "overall_confidence": 85,
                "reasoning": "Clear pattern of database connectivity issues with cascading effects",
                "areas_of_uncertainty": [
                    "Root cause of initial database timeout"
                ]
            },
            "escalation_criteria": {
                "escalate_if": [
                    "Database server remains unreachable after 15 minutes",
                    "Customer impact continues beyond 30 minutes"
                ],
                "suggested_contacts": ["Database Team", "Platform Engineering"]
            }
        }

    def _generate_fallback_analysis(self, logs: List[LogEntry]) -> Dict:
        """Generate basic fallback analysis when AI fails"""
        return {
            "incident_classification": {
                "severity": "P3",
                "category": "Analysis Failed",
                "impact_assessment": "Unable to determine impact - manual review required",
                "affected_services": ["unknown"]
            },
            "root_cause_analysis": {
                "primary_cause": "AI analysis failed - manual investigation required",
                "contributing_factors": ["Analysis system error"],
                "evidence_summary": "Could not process logs automatically",
                "log_citations": []
            },
            "resolution_guidance": {
                "immediate_actions": ["Manual log review required"],
                "step_by_step_remediation": [],
                "preventive_measures": ["Improve log analysis system reliability"]
            },
            "confidence_assessment": {
                "overall_confidence": 0,
                "reasoning": "Analysis system failed",
                "areas_of_uncertainty": ["All areas require manual review"]
            },
            "escalation_criteria": {
                "escalate_if": ["Immediately"],
                "suggested_contacts": ["Senior SRE", "Platform Engineering"]
            }
        }

gemini_analyzer = GeminiAnalyzer(config)
print("🤖 Gemini analyzer initialized")

## 4. LangChain Agent Tools

# Define tools for the agent
@tool
def parse_log_entries(log_data: str) -> str:
    """Parse raw log data into structured log entries"""

    lines = log_data.strip().split('\n')
    parsed_logs = []

    for line in lines:
        if line.strip():
            log_entry = LogEntry(line.strip(), source="manual_input")
            parsed_logs.append(log_entry.to_dict())

    return json.dumps(parsed_logs, indent=2)

@tool
def classify_incident_severity(logs_json: str) -> str:
    """Classify incident severity based on parsed logs"""

    try:
        logs_data = json.loads(logs_json)

        # Simple rule-based classification
        has_critical = any(log.get('severity') == 'CRITICAL' for log in logs_data)
        has_error = any(log.get('severity') == 'ERROR' for log in logs_data)
        error_count = sum(1 for log in logs_data if log.get('severity') in ['ERROR', 'CRITICAL'])

        if has_critical or error_count >= 3:
            severity = "P1 - Critical"
        elif has_error:
            severity = "P2 - High"
        else:
            severity = "P3 - Medium"

        return f"Incident Severity: {severity} (based on {len(logs_data)} log entries)"

    except Exception as e:
        return f"Error classifying severity: {str(e)}"

@tool
def search_similar_incidents(incident_hash: str) -> str:
    """Search for similar historical incidents (simulated)"""

    # Simulated historical incident database
    similar_incidents = [
        {
            "incident_id": "INC-2024-1234",
            "similarity_score": 0.85,
            "resolution_time": "45 minutes",
            "root_cause": "Database connection pool exhaustion",
            "resolution": "Increased connection pool size and restarted services"
        },
        {
            "incident_id": "INC-2024-0987",
            "similarity_score": 0.72,
            "resolution_time": "2 hours",
            "root_cause": "MySQL server memory leak",
            "resolution": "Restarted MySQL server and applied memory patches"
        }
    ]

    return json.dumps(similar_incidents, indent=2)

@tool
def check_service_dependencies(service_name: str) -> str:
    """Check service dependencies and health status"""

    # Simulated service dependency map
    dependencies = {
        "webapp": ["database", "auth-service", "cache"],
        "database": ["storage", "network"],
        "auth-service": ["database", "ldap"],
        "payment-gateway": ["webapp", "external-payment-api", "database"]
    }

    service_deps = dependencies.get(service_name, [])

    # Simulated health checks
    health_status = {}
    for dep in service_deps:
        health_status[dep] = np.random.choice(["healthy", "degraded", "unhealthy"], p=[0.7, 0.2, 0.1])

    return json.dumps({
        "service": service_name,
        "dependencies": service_deps,
        "health_status": health_status
    }, indent=2)

@tool
def generate_incident_report(analysis_json: str) -> str:
    """Generate formatted incident report"""

    try:
        analysis = json.loads(analysis_json)

        report = f"""
# INCIDENT RESPONSE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

           ## Incident Classification
           - ** Severity **: {analysis.get('incident_classification', {}).get('severity', 'Unknown')}
                             - ** Category **: {analysis.get('incident_classification', {}).get('category', 'Unknown')}
                                               - ** Affected
Services **: {', '.join(analysis.get('incident_classification', {}).get('affected_services', []))}

             ## Root Cause Analysis
             - ** Primary
Cause **: {analysis.get('root_cause_analysis', {}).get('primary_cause', 'Under investigation')}
          - ** Contributing
Factors **:
"""

        for factor in analysis.get('root_cause_analysis', {}).get('contributing_factors', []):
            report += f"  - {factor}\n"

        report += f"""
## Immediate Actions Required
"""
        for action in analysis.get('resolution_guidance', {}).get('immediate_actions', []):
            report += f"- [ ] {action}\n"

        report += f"""
## Resolution Steps
"""
        for step in analysis.get('resolution_guidance', {}).get('step_by_step_remediation', []):
            report += f"{step.get('step', 0)}. {step.get('action', '')}\n"
            report += f"   Expected: {step.get('expected_outcome', '')}\n\n"

        report += f"""
## Confidence Assessment
- ** Overall
Confidence **: {analysis.get('confidence_assessment', {}).get('overall_confidence', 0)} %
               - ** Reasoning **: {analysis.get('confidence_assessment', {}).get('reasoning', 'No reasoning provided')}
"""

        return report

    except Exception as e:
        return f"Error generating report: {str(e)}"

# Create tool list
tools = [
    parse_log_entries,
    classify_incident_severity,
    search_similar_incidents,
    check_service_dependencies,
    generate_incident_report
]

print("🛠️  Agent tools configured")

## 5. LangChain Agent Setup

# Agent prompt template
agent_prompt = PromptTemplate.from_template("""
You
are
Scooby, an
expert
Site
Reliability
Engineer(SRE)
AI
agent
specializing in automated
incident
response and log
analysis.

Your
mission: Analyze
system
logs, identify
incidents, and provide
actionable
resolution
guidance
with high confidence and speed.

** Your Capabilities:**
- Parse and analyze
system
logs
from multiple sources

- Classify
incident
severity(P0 - P3)
based
on
impact and urgency
- Search
historical
incidents
for similar patterns
            - Check service dependencies and health status
- Generate comprehensive incident response reports

** Analysis Framework:**
1. ** Parse
Logs **: Structure
raw
log
data
for analysis
2. ** Classify Severity **: Determine
incident
priority
level
3. ** Root
Cause
Analysis **: Identify
primary and contributing
factors
4. ** Search
History **: Find
similar
past
incidents and resolutions
5. ** Dependency
Check **: Assess
affected
services and dependencies
6. ** Generate
Report **: Create
actionable
incident
response
documentation

** Available
Tools: **
{tools}

** Tool
Usage
Guidelines: **
- Always
start
by
parsing
raw
logs
into
structured
format
- Classify
severity
early
to
determine
response
urgency
- Search
for similar incidents to leverage past resolutions
- Check dependencies to understand full impact scope
- Generate comprehensive reports for incident documentation

** Response Format:**
- Be
concise
but
thorough in your
analysis
- Provide
specific, actionable
recommendations
- Include
confidence
levels
for your assessments
         - Cite specific log entries as evidence
- Focus on minimizing mean time to resolution (MTTR)

Use the following format:

    Question: the
input
question
you
must
answer
Thought: you
should
always
think
about
what
to
do
Action: the
action
to
take, should
be
one
of[{tool_names}]
Action
Input: the
input
to
the
action
Observation: the
result
of
the
action
...(this
Thought / Action / Action
Input / Observation
can
repeat
N
times)
Thought: I
now
know
the
final
answer
Final
Answer: the
final
answer
to
the
original
input
question

Begin!

Question: {input}
{agent_scratchpad}
""")

# Real Gemini LLM for agent reasoning
class GeminiLLM:
    """
Real
Gemini
LLM
integration
for LangChain agent"""

    def __init__(self, config: ScoobyConfig):
        self.config = config
        self.model = config.model

        if not self.model:
            raise Exception("Gemini model not initialized. Please set GEMINI_API_KEY.")

    def __call__(self, prompt: str) -> str:
        """Generate response using Gemini 2.0 Flash"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Slightly higher for reasoning
                    top_p=0.9,
                    max_output_tokens=1024,
                )
            )
            return response.text

        except Exception as e:
            print(f"❌ Gemini LLM error: {e}")
            # Return a simple fallback that follows the agent format
            return """Thought: I
encountered
an
error
with the AI reasoning system.
Final Answer: I
apologize, but
I
'm unable to process this request due to a technical issue with the AI reasoning system. Please ensure your Gemini API key is properly configured and try again."""

# Create memory for conversation history
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,  # Remember last 5 interactions
    return_messages=True
)

print("🧠 Agent memory and LLM configured")

## 🔑 IMPORTANT: Gemini API Key Setup

print("\n" + "=" * 60)
print("🔑 GEMINI API KEY SETUP REQUIRED")
print("=" * 60)

if not config.gemini_api_key:
    print("""
❌ No Gemini API key found!

To use Scooby with real Gemini 2.0 Flash analysis:

1. Get your API key from Google AI Studio:
   👉 https://aistudio.google.com/app/apikey

2. Set your API key in this notebook:

   # Set your actual Gemini API key here
   import os
   os.environ['GEMINI_API_KEY'] = 'your-actual-gemini-api-key-here'

   # Then reinitialize the config
   config = ScoobyConfig()
   gemini_analyzer = GeminiAnalyzer(config)

3. Or set it as an environment variable:
   export GEMINI_API_KEY="your-actual-gemini-api-key-here"

⚠️  Without a valid API key, the system cannot provide real log analysis!
""")
else:
    print(f"✅ Gemini API key configured (ends with: ...{config.gemini_api_key[-8:]})")
if config.model:
    print("✅ Gemini 2.0 Flash model ready for analysis")
else:
    print("❌ Gemini model initialization failed")

print("=" * 60)

## 6. Main Scooby Agent Class


class ScoobyAgent:
    """Main Scooby agent for incident response"""

    def __init__(self, tools: List[Tool], gemini_analyzer: GeminiAnalyzer):
        self.tools = tools
        self.gemini_analyzer = gemini_analyzer

        # Use real Gemini LLM for agent reasoning
        try:
            self.llm = GeminiLLM(config)
            print("✅ Real Gemini LLM initialized for agent reasoning")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini LLM: {e}")
            print("   Agent reasoning will be limited without proper Gemini setup")
            self.llm = None

        # Create the agent only if LLM is available
        if self.llm:
            self.agent = create_react_agent(
                llm=self.llm,
                tools=tools,
                prompt=agent_prompt
            )

            # Create executor
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=tools,
                memory=memory,
                verbose=True,
                max_iterations=10,
                handle_parsing_errors=True
            )
        else:
            self.agent = None
            self.agent_executor = None

        self.incident_counter = 0

    async def analyze_incident(self, raw_logs: str, context: Dict = None) -> Dict:
        """Main method to analyze an incident"""

        if not self.gemini_analyzer.model:
            raise Exception("""
❌ Gemini 2.0 Flash not available!

To use Scooby with real analysis, you need to:
1. Install Google AI SDK: pip install google-generativeai
2. Get a Gemini API key from: https://makersuite.google.com/app/apikey
3. Set the API key: os.environ['GEMINI_API_KEY'] = 'your-actual-api-key'

Without a valid API key, Scooby cannot provide intelligent log analysis.
""")

        self.incident_counter += 1
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{self.incident_counter:04d}"

        print(f"🚨 Starting incident analysis: {incident_id}")
        print(f"📋 Processing {len(raw_logs.split(chr(10)))} log entries")

        # Step 1: Parse logs
        log_entries = []
        for line in raw_logs.strip().split('\n'):
            if line.strip():
                log_entry = LogEntry(line.strip(), source="incident_input")
                log_entries.append(log_entry)

        # Step 2: Use Gemini for detailed analysis
        try:
            print("🤖 Running Gemini 2.0 Flash analysis...")
            gemini_analysis = await self.gemini_analyzer.analyze_logs(log_entries, context)
            print("✅ Gemini analysis completed successfully")

        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            raise Exception(f"Failed to analyze logs with Gemini: {e}")

        # Step 3: Agent-based workflow for additional insights (if available)
        agent_result = "Agent analysis not available - Gemini LLM required"

        if self.agent_executor:
            agent_input = f"""
Analyze this incident with ID {incident_id}:

Raw Logs:
{raw_logs}

Context: {json.dumps(context or {}, indent=2)}

Please provide a comprehensive incident response analysis following the SRE best practices.
"""

            try:
                print("🔧 Running agent-based analysis...")
                agent_response = self.agent_executor.invoke({"input": agent_input})
                agent_result = agent_response.get("output", "Agent analysis completed")
                print("✅ Agent analysis completed")

            except Exception as e:
                print(f"⚠️  Agent analysis failed: {str(e)}")
                agent_result = f"Agent analysis failed: {str(e)}"

        # Step 4: Combine results
        final_analysis = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "gemini_analysis": gemini_analysis,
            "agent_insights": agent_result,
            "log_summary": {
                "total_entries": len(log_entries),
                "severity_breakdown": self._get_severity_breakdown(log_entries),
                "affected_services": list(set(log.service for log in log_entries if log.service != "unknown")),
                "time_span": self._get_time_span(log_entries)
            },
            "recommendations": self._generate_recommendations(gemini_analysis),
            "next_steps": self._generate_next_steps(gemini_analysis)
        }

        print(f"✅ Incident analysis complete: {incident_id}")
        return final_analysis

    def _get_severity_breakdown(self, logs: List[LogEntry]) -> Dict:
        """Get breakdown of log severities"""
        breakdown = {}
        for log in logs:
            breakdown[log.severity] = breakdown.get(log.severity, 0) + 1
        return breakdown

    def _get_time_span(self, logs: List[LogEntry]) -> Dict:
        """Get time span of incident"""
        timestamps = [log.timestamp for log in logs if log.timestamp]
        if timestamps:
            return {
                "start": min(timestamps).isoformat(),
                "end": max(timestamps).isoformat(),
                "duration_minutes": (max(timestamps) - min(timestamps)).total_seconds() / 60
            }
        return {}

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        severity = analysis.get('incident_classification', {}).get('severity', 'P3')

        if severity in ['P0', 'P1']:
            recommendations.extend([
                "🚨 CRITICAL: Immediate escalation required",
                "📞 Notify on-call engineer and incident commander",
                "📊 Set up incident war room for coordination"
            ])

        immediate_actions = analysis.get('resolution_guidance', {}).get('immediate_actions', [])
        recommendations.extend([f"⚡ {action}" for action in immediate_actions])

        return recommendations

    def _generate_next_steps(self, analysis: Dict) -> List[Dict]:
        """Generate structured next steps"""
        steps = []

        remediation_steps = analysis.get('resolution_guidance', {}).get('step_by_step_remediation', [])

        for step_info in remediation_steps:
            steps.append({
                "step": step_info.get('step', 0),
                "action": step_info.get('action', ''),
                "expected_outcome": step_info.get('expected_outcome', ''),
                "estimated_time": "5-15 minutes",  # Default estimate
                "assigned_to": "On-call SRE",
                "status": "pending"
            })

        return steps


# Initialize the main agent
scooby_agent = ScoobyAgent(tools, gemini_analyzer)
print("🐕 Scooby agent fully initialized and ready!")


## 7. Demo Workflow and Testing

async def run_incident_analysis_demo():
    """Demonstrate the complete incident analysis workflow"""

    print("\n" + "=" * 60)
    print("🚨 SCOOBY INCIDENT ANALYSIS DEMO")
    print("=" * 60)

    # Check if Gemini is properly configured
    if not config.model:
        print("""
❌ Cannot run demo - Gemini 2.0 Flash not configured!

Please set up your Gemini API key first:

# Set your API key
import os
os.environ['GEMINI_API_KEY'] = 'your-actual-gemini-api-key-here'

# Reinitialize the system
config = ScoobyConfig()
gemini_analyzer = GeminiAnalyzer(config)
scooby_agent = ScoobyAgent(tools, gemini_analyzer)

# Then run the demo
demo_result = await run_incident_analysis_demo()
        """)
        return None

    # Sample incident logs
    incident_logs = "\n".join(SAMPLE_LOGS)

    # Additional context
    incident_context = {
        "reported_by": "Monitoring System",
        "affected_users": "~500 users",
        "business_impact": "Payment processing down",
        "environment": "production",
        "region": "us-east-1"
    }

    print("\n📋 Raw Incident Logs:")
    print("-" * 40)
    for i, log in enumerate(SAMPLE_LOGS, 1):
        print(f"{i}. {log}")

    print(f"\n🔍 Context Information:")
    for key, value in incident_context.items():
        print(f"   {key}: {value}")

    # Run the analysis
    print(f"\n🤖 Running Scooby Analysis with Gemini 2.0 Flash...")

    try:
        analysis_result = await scooby_agent.analyze_incident(incident_logs, incident_context)

        # Display results
        print(f"\n📊 ANALYSIS RESULTS")
        print("-" * 40)

        print(f"🆔 Incident ID: {analysis_result['incident_id']}")
        print(f"⏰ Analysis Time: {analysis_result['timestamp']}")

        # Gemini Analysis Results
        gemini_analysis = analysis_result['gemini_analysis']
        classification = gemini_analysis.get('incident_classification', {})

        print(f"\n🎯 INCIDENT CLASSIFICATION")
        print(f"   Severity: {classification.get('severity', 'Unknown')}")
        print(f"   Category: {classification.get('category', 'Unknown')}")
        print(f"   Impact: {classification.get('impact_assessment', 'Unknown')}")
        print(f"   Services: {', '.join(classification.get('affected_services', []))}")

        # Root Cause
        root_cause = gemini_analysis.get('root_cause_analysis', {})
        print(f"\n🔍 ROOT CAUSE ANALYSIS")
        print(f"   Primary Cause: {root_cause.get('primary_cause', 'Unknown')}")
        print(f"   Contributing Factors:")
        for factor in root_cause.get('contributing_factors', []):
            print(f"      - {factor}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        for rec in analysis_result.get('recommendations', []):
            print(f"   {rec}")

        # Next Steps
        print(f"\n📋 NEXT STEPS")
        for step in analysis_result.get('next_steps', []):
            print(f"   {step['step']}. {step['action']}")
            print(f"      Expected: {step['expected_outcome']}")
            print(f"      Time: {step['estimated_time']}")
            print()


    return analysis_result

# Run the demo
demo_result = await run_incident_analysis_demo()

# Final demonstration with actual log parsing
sample_log = "2025-01-15 16:45:12 CRITICAL [payment-service] Payment gateway timeout: external API unreachable after 30s retry_count=3 transaction_id=txn_999888"
sample_entry = LogEntry(sample_log, source="demo", service="payment-service")

