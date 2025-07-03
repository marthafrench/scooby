# scooby
An AI-powered incident response system that analyses Splunk logs with Gemini 2.0 Flash via PyTorch to provide intelligent root cause analysis and automated resolution guidance

## Overview

This project implements an AI-powered system that automatically analyses system failure logs from Splunk, provides intelligent insights about incidents, and presents actionable information through automated dashboards. The system combines log aggregation, machine learning analysis, and intelligent prompt management to transform raw failure data into comprehensive incident response guidance.

## What We Want to Achieve

**Primary Objectives:**
- Automatically detect and categorise system failures across multiple services
- Provide instant, intelligent analysis of incidents including root cause identification
- Generate actionable remediation steps and escalation paths
- Reduce mean time to resolution (MTTR) for incidents
- Enable self-service incident resolution for common issues
- Create a knowledge base that evolves with each incident

## User Personas & Use Cases

### Primary Users

**First Line Support**
- **Needs**: Quick incident understanding, clear resolution steps, escalation guidance
- **Benefits**: AI-powered dashboard provides immediate context, suggested fixes, and confidence scoring
- **Workflow**: Receives alert → Reviews AI analysis → Follows guided resolution → Escalates if needed

**DevOps Engineer**  
- **Needs**: Proactive issue detection, technical root cause analysis, remediation automation
- **Benefits**: Early warnings about emerging patterns, detailed technical analysis, infrastructure-specific recommendations
- **Workflow**: Monitors trends → Receives AI alerts → Reviews suggested fixes → Implements preventive measures

**Incident Manager**
- **Needs**: Cross-service incident coordination, impact assessment, stakeholder communication
- **Benefits**: AI-generated executive summaries, similar incident history, business impact analysis
- **Workflow**: Major incident declared → Reviews AI context → Coordinates response → Tracks resolution

**SRE Lead**
- **Needs**: System reliability insights, log quality improvement, incident pattern analysis
- **Benefits**: Log quality scoring, trend analysis, preventive recommendations, team performance metrics
- **Workflow**: Reviews monthly patterns → Identifies improvement areas → Tunes system settings → Drives process changes

## Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Splunk    │───▶│  SPL Query   │───▶│  Python App     │
│ (Log Source)│    │ (Filtering)  │    │ (Log Parser)    │
└─────────────┘    └──────────────┘    └─────────────────┘
                                                │
                                                ▼
┌─────────────┐                        ┌─────────────────┐
│   LangChain │───────────────────────▶│   PyTorch +     │
│ (Prompt Mgmt)│                       │   Gemini AI     │
└─────────────┘                        └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   Splunk        │
                                        │  (Results)      │
                                        └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   Dashboard     │
                                        │ (Visualization) │
                                        └─────────────────┘
```

### Core Components

1. **Splunk**: Custom Splunk queries to identify and extract failure patterns
   - Automated log filtering and classification
   - Multi-service failure correlation
   - Real-time and historical pattern detection

2. **Python Log Parser**: Processes extracted logs and prepares data for AI analysis
   - Log normalisation and standardisation
   - Metadata enrichment and tagging
   - Batch processing optimisation

3. **PyTorch + Gemini 2.0 Flash Integration**: Analyses patterns and generates insights
   - Parallel processing of multiple log entries
   - Advanced reasoning and root cause analysis
   - Confidence scoring and explanation generation

4. **LangChain Prompt Management**: Manages AI prompts and response formatting
   - Version-controlled prompt templates
   - Context-aware prompt generation
   - Response consistency and quality control

5. **Splunk Dashboard**: Presents insights to support teams
   - Real-time incident visualisation
   - Historical trend analysis
   - Interactive drill-down capabilities

6. **Knowledge Base Integration**: Links to internal documentation and expert contacts
   - Automated documentation lookup
   - Expert identification and routing
   - Continuous knowledge base updates

## Business Benefits

### Quantified Impact Targets
- **40-60% reduction** in first-line support ticket volume through automated resolution guidance
- **50% improvement** in average incident resolution time via immediate root cause identification
- **>90% accuracy** in initial incident classification and severity assessment
- **70% self-service resolution rate** for common incidents without escalation

### Operational Excellence
**Cost Reduction**: Lower support costs through reduced first line expansion needs and minimised business downtime. Training efficiency improved as new team members resolve incidents with AI guidance.

**Resource Optimisation**: Support staff focus on complex issues rather than routine troubleshooting. Developer teams receive contextualised alerts reducing investigation time.

**Knowledge Management**: Institutional knowledge capture through AI learning from each incident. Consistent response quality with standardised analysis reducing human error. Continuous improvement as system evolves with organisational knowledge.

**Scalability**: System handles increasing log volumes without linear resource growth, providing uniform analysis quality regardless of support staff experience level.

## Technical Implementation

### Phase 1: Log Extraction & Processing
```spl
index=application_logs OR index=system_logs 
| search (ERROR OR FATAL OR CRITICAL OR "Exception" OR "Failed")
| eval service=case(
    match(source, "service-a"), "Service A",
    match(source, "service-b"), "Service B",
    1=1, "Unknown"
)
| table _time, host, service, message, severity
```

### Phase 2: AI Analysis Pipeline
- **Input Processing**: Structured log data from Splunk
- **Parallel Processing**: Multiple log entries analysed concurrently via Gemini 2.0 Flash API
- **Pattern Recognition**: PyTorch models identify failure signatures
- **Context Enhancement**: Gemini 2.0 Flash provides fast, detailed analysis with intelligent batch processing
- **Response Generation**: LangChain manages prompt templates for consistent outputs
- **Rate Management**: Optimised for Gemini 2.0 Flash (Free: 15 RPM, Paid Tier 1: 2,000 RPM, Tier 2: 10,000 RPM)

### Phase 3: Dashboard Integration & Feedback Loop
- Real-time incident classification
- Automated root cause analysis
- Suggested remediation steps
- Expert contact information
- Historical pattern analysis
- **Interactive Feedback System**: User validation with CoT persistence

#### Technical Implementation of Feedback System

**Dashboard Panel Structure**:
```xml
<panel>
  <title>AI Analysis Results</title>
  <html>
    <div id="ai-analysis-$incident_id$">
      <h3>Root Cause Analysis</h3>
      <p>$ai_analysis$</p>
      
      <h4>Chain of Thought</h4>
      <div class="cot-reasoning">$chain_of_thought$</div>
      
      <div class="feedback-buttons">
        <button class="btn-correct" onclick="submitFeedback('$incident_id$', 'correct')">
          ✓ Correct Analysis
        </button>
        <button class="btn-incorrect" onclick="submitFeedback('$incident_id$', 'incorrect')">
          ✗ Incorrect Analysis
        </button>
      </div>
    </div>
  </html>
</panel>
```

**JavaScript Implementation**:
```javascript
function submitFeedback(incidentId, feedbackType) {
    // Gather feedback data
    const feedbackData = {
        incident_id: incidentId,
        feedback_type: feedbackType,
        user: Splunk.util.getUsername(),
        timestamp: new Date().toISOString(),
        ai_analysis: document.querySelector(`#ai-analysis-${incidentId} p`).textContent,
        chain_of_thought: document.querySelector(`#ai-analysis-${incidentId} .cot-reasoning`).textContent,
        original_logs: getOriginalLogs(incidentId)
    };
    
    // Send to Splunk REST API
    fetch('/servicesNS/nobody/scooby_app/storage/collections/data/ai_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Splunk ' + Splunk.util.getToken()
        },
        body: JSON.stringify(feedbackData)
    })
    .then(response => response.json())
    .then(data => {
        // Update UI to show feedback was recorded
        showFeedbackConfirmation(incidentId, feedbackType);
        
        // If correct, save to knowledge base index
        if (feedbackType === 'correct') {
            indexSuccessfulCoT(feedbackData);
        }
    });
}
```

**Splunk Index Structure for Feedback**:
```
# Index: ai_feedback
{
    "incident_id": "INC-2025-001",
    "feedback_type": "correct",
    "user": "support.analyst",
    "timestamp": "2025-01-15T10:30:45.000Z",
    "ai_analysis": "Root cause identified as database connection pool exhaustion...",
    "chain_of_thought": "1. Analysed error patterns... 2. Identified correlation with... 3. Concluded that...",
    "original_logs": [...],
    "resolution_outcome": "successful",
    "resolution_time_minutes": 12
}
```

**Knowledge Base Integration**:
```python
# Python service component
def save_validated_cot(feedback_data):
    """Save validated Chain of Thought to knowledge base"""
    if feedback_data['feedback_type'] == 'correct':
        knowledge_entry = {
            'log_pattern': extract_log_pattern(feedback_data['original_logs']),
            'successful_analysis': feedback_data['ai_analysis'],
            'reasoning_chain': feedback_data['chain_of_thought'],
            'validation_count': 1,
            'last_validated': feedback_data['timestamp'],
            'success_rate': 1.0
        }
        
        # Index in Splunk knowledge base
        splunk_client.index('ai_knowledge_base').submit(json.dumps(knowledge_entry))
        
        # Update RAG embeddings for future queries
        update_rag_embeddings(knowledge_entry)
```

**Dashboard Query for Feedback Analytics**:
```spl
index=ai_feedback 
| stats count by feedback_type, user, date_trunc=1d 
| eval success_rate = round(correct/(correct+incorrect)*100, 2)
| table _time, user, success_rate, total_feedback
```

**Benefits of This Approach**:
- **Seamless Integration**: Buttons appear directly in existing Splunk dashboards
- **Automatic Learning**: Correct CoT reasoning is immediately saved for future reference
- **Audit Trail**: Complete tracking of user feedback and validation history
- **Continuous Improvement**: System learns from validated successful analyses
- **User Engagement**: Simple one-click feedback encourages participation

### Gemini 2.0 Flash Tier Comparison

| Tier | RPM Limit | TPM Limit | Cost | Best For |
|------|-----------|-----------|------|----------|
| **Free** | **15** | **1M** | $0 | Proof of concept, small teams |
| **Paid Tier 1** | **2,000** | **4M** | Pay-per-use | Production deployment, medium scale |
| **Paid Tier 2** | **10,000** | **10M** | Pay-per-use | Enterprise scale, high-volume incidents |
| **Paid Tier 3** | **30,000** | **30M** | Pay-per-use | Large enterprise, multi-tenant systems |

**Capacity Planning Guide**:
- **Free Tier**: Handles ~**20** small incidents/day
- **Tier 1**: Supports ~**50-100** concurrent incidents  
- **Tier 2**: **Enterprise-grade** incident response at scale
- **Tier 3**: **Multi-organisation** or very high-volume environments

## Pros and Cons

### Advantages
- **Scalability**: Handles increasing log volumes without linear resource growth
- **Consistency**: Provides uniform analysis quality regardless of support staff experience
- **Learning Capability**: Improves over time with more data and feedback
- **Integration**: Leverages existing Splunk infrastructure
- **Cost-Effective**: Utilises cloud-based AI services without significant infrastructure investment

### Challenges
- **Initial Setup Complexity**: Requires careful tuning of SPL queries and AI prompts
- **Data Quality Dependency**: Effectiveness limited by log quality and consistency
- **AI Model Accuracy**: May require ongoing training and refinement
- **Change Management**: Teams need to adapt to new workflows and trust AI recommendations
- **Maintenance Overhead**: Requires ongoing monitoring and prompt optimisation

## Critical Areas to Watch & Improve

### 1. AI Model Risk Management
**Challenge**: LLM reliability in high-stakes incident response requires robust safety measures.

**Mitigation Strategies**:
- **Prompt Versioning & Audit**: Implement Git-based prompt management with full audit trails
- **Confidence Scoring**: Require Gemini to provide confidence levels (0-100%) for all recommendations
- **Explanation Requirements**: Force AI to cite specific log entries and reasoning for each conclusion
- **Human-in-the-Loop Workflows**: Mandatory human validation for:
  - Critical severity incidents (P0/P1)
  - Recommendations involving infrastructure changes
  - New failure patterns not seen in training data
- **Fallback Mechanisms**: Automatic escalation to human experts when confidence < 70%

### 2. Data Quality Challenges
**Challenge**: Inconsistent logging practices across teams will degrade AI performance.

**Solutions**:
- **Log Quality Scoring**: Implement automated scoring based on:
  - Structured vs unstructured content ratio
  - Presence of key fields (timestamp, severity, service, error codes)
  - Message consistency and standardisation
- **Developer Partnership Programme**: 
  - Quarterly log quality reviews with dev teams
  - Standardised logging libraries and templates
  - Log quality dashboards for team leads
- **Progressive Enhancement**: Start with highest-quality log sources, expand gradually
- **Log Enrichment Pipeline**: Automated tagging and standardisation where possible

### 3. Dual-Mode Processing Architecture
**Challenge**: AI analysis may introduce unacceptable delays in critical incident response.

```
                    ┌─────────────────┐
                    │  Incident Log   │
                    │    Detected     │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   Severity      │
                    │  Classification │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   P0/P1/P2?     │
                    └─────────┬───────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
    ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Fast-Path    │ │ Fast-Path    │ │ Deep AI      │
    │   Triage      │ │  Triage      │ │  Analysis    │
    │  (P0: <3s)    │ │ (P1: <5s)    │ │ (P2+: 30-60s)│
    └───────┬───────┘ └──────┬───────┘ └──────┬───────┘
            │                │                │
            ▼                ▼                ▼
    ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Immediate     │ │ Rule-Based   │ │ Gemini 2.0   │
    │ Escalation    │ │ Resolution   │ │ Flash        │
    │ + Runbook     │ │ Suggestions  │ │ Full Analysis│
    └───────────────┘ └──────────────┘ └──────────────┘
```

**Processing Modes**:
- **Fast-Path Triage** (P0/P1: < 5 seconds): Rule-based classification, immediate escalation, basic runbook suggestions from lookup tables
- **Deep AI Analysis** (P2+: 30-60 seconds): Full Gemini 2.0 Flash processing with parallel batch processing, complex root cause analysis, historical pattern matching
- **Async Enhancement**: AI insights delivered as follow-up notifications for all incident types

**Parallel Processing Benefits with Gemini 2.0 Flash**:
- **Free Tier**: Process up to 15 log entries per minute (1M tokens/minute)
- **Paid Tier 1**: Process up to 2,000 log entries per minute with 4M tokens/minute  
- **Paid Tier 2**: Scale to 10,000 requests per minute with 10M tokens/minute for enterprise incidents
- **Speed Optimised**: Gemini 2.0 Flash designed for low-latency responses ideal for incident response
- **Cost Effective**: Best price-to-performance ratio for high-volume log analysis
- **Multimodal Ready**: Can analyse log screenshots, dashboards, and charts alongside text logs

### 4. Integration as First-Class Features
**Challenge**: Poor integration with existing workflows will limit adoption.

**Integration Strategy**:
- **Splunk-Focused Integration**: Leverage existing Splunk infrastructure and team expertise
  - Utilise existing Splunk knowledge base and documentation repositories
  - Build on current support team familiarity with Splunk interfaces
  - Integrate with established Splunk dashboards and visualisation workflows
  - Maintain consistency with existing security and access control frameworks
- **Enhanced Splunk Capabilities**: 
  - AI-powered insights displayed within familiar Splunk dashboard environment
  - Results stored in Splunk indexes for consistent data governance
  - Search and reporting capabilities for AI analysis history
  - Integration with existing Splunk alerting and notification systems
- **Feedback Loop Implementation**:
  - Interactive "Correct" and "Incorrect" buttons within Splunk dashboard panels
  - Chain-of-Thought (CoT) reasoning automatically saved when users validate responses
  - Feedback data indexed in dedicated Splunk index for continuous learning
  - User attribution and timestamp tracking for audit and improvement purposes
- **API-First Design**: All features accessible via REST APIs for future integrations as requirements evolve

## Advanced Capabilities & Opportunities

### Retrieval-Augmented Generation (RAG)
**Implementation**: Enhance AI prompts with contextual data from:
- Historical incident database (past 12 months)
- Internal documentation and runbooks  
- Expert resolution notes and post-mortems
- Service dependency maps and topology data

**Benefits**: More accurate, context-aware recommendations based on organisational knowledge

### Incident Similarity Engine
**Functionality**:
- Semantic similarity scoring using vector embeddings
- "Similar incidents resolved in the past" suggestions
- Success rate tracking for recommended solutions
- Learning from resolution outcomes

**UI Integration**: Side panel showing top 3 similar incidents with resolution times and steps

### Explainability & Trust Building
**Requirements**:
- **Evidence Links**: Every AI recommendation must link to specific log entries
- **Reasoning Chain**: Step-by-step explanation of analysis logic
- **Confidence Breakdown**: Separate confidence scores for detection, classification, and remediation
- **Documentation References**: Auto-link to relevant internal docs and procedures

### Executive Reporting
**"Why This Alert Matters" Summaries**:
- Business impact assessment in non-technical terms
- Customer/revenue impact estimates
- Resource allocation recommendations
- Trend analysis and prevention opportunities

## Technology Stack Decisions

### MVP Implementation Strategy
**Decision**: Build MVP in Python, with technology stack reevaluation post-MVP.

**Rationale**: 
- Python offers rapid prototyping capabilities for AI/ML integrations
- Extensive library ecosystem (PyTorch, LangChain, Splunk SDK)
- Team familiarity and quick time-to-value
- Post-MVP evaluation will consider performance requirements and scale needs

### Architecture Alternatives Considered

#### Option 1: Native Splunk AI Implementation
**Why Discounted**:
- **Resource Burden**: Additional CPU and memory load on existing Splunk infrastructure
- **Cost Impact**: Splunk licensing costs scale with compute usage - AI processing would significantly increase operational expenses
- **Limited AI Capabilities**: Splunk's native AI features don't match Gemini 2.0 Flash's advanced reasoning and natural language capabilities
- **Vendor Lock-in**: Reduces flexibility for future AI model upgrades or vendor changes
- **Performance Constraints**: Splunk optimised for search/indexing, not intensive AI workloads

#### Option 2: Custom UI + Separate Database
**Why Discounted**:
- **Security Overhead**: Requires building entire authentication, authorisation, and audit infrastructure from scratch
- **Licensing Efficiency**: Support teams already have Splunk access - no additional licence provisioning needed
- **Development Complexity**: Significant frontend development effort diverts resources from core AI functionality
- **User Adoption**: Support teams already familiar with Splunk interface - reduces training overhead
- **Maintenance Burden**: Additional infrastructure to monitor, backup, and maintain

#### Option 3: Alternative Cloud AI Services
**Comparison Analysis**:

| Provider | Discounted Because |
|----------|-------------------|
| **OpenAI GPT-4** | Higher latency, more expensive for high-volume processing, less granular rate limiting |
| **AWS Bedrock** | More complex setup, requires additional AWS infrastructure, limited customisation |
| **Azure OpenAI** | Enterprise focus increases complexity, higher costs, less suitable for rapid prototyping |
| **Local LLM (Llama, etc.)** | Significant infrastructure investment, model management overhead, limited reasoning capabilities |

### Why This Stack: Splunk + Python + Gemini 2.0 Flash

#### Splunk Integration Benefits
- **Existing Infrastructure**: Leverage current log aggregation and storage investment
- **User Familiarity**: Support teams already trained on Splunk interfaces
- **Data Quality**: Logs already normalised and indexed for efficient querying
- **Security**: Inherits existing access controls, audit trails, and compliance frameworks
- **Scalability**: Proven ability to handle enterprise-scale log volumes

#### Python Advantages for MVP
- **AI/ML Ecosystem**: Native integration with PyTorch, LangChain, transformers libraries
- **Rapid Development**: Quick iteration cycles for prompt engineering and model integration
- **Team Skills**: Existing Python expertise within organisation
- **Splunk SDK**: Mature, well-documented Python SDK for Splunk integration
- **Community Support**: Large community for troubleshooting AI integration challenges

#### Gemini 2.0 Flash Selection
- **Performance**: Low-latency responses critical for incident response scenarios
- **Cost Efficiency**: Best price-to-performance ratio for high-volume log processing
- **Reasoning Capability**: Superior logical reasoning for root cause analysis
- **Multimodal Ready**: Future capability to process screenshots and visual incident data
- **Rate Limits**: Generous limits support enterprise-scale incident volumes
- **API Maturity**: Stable, well-documented API with robust error handling

### Strategic Technology Goals

#### Skill Development Initiative
**Objective**: Build organisational capability in AI application development.

**Benefits**:
- **Future-Proofing**: Embed AI skills across development teams for future projects
- **Knowledge Transfer**: Create internal expertise rather than external consulting dependency
- **Innovation Culture**: Encourage experimentation with AI-powered solutions
- **Competitive Advantage**: Develop proprietary AI integration capabilities
- **Career Development**: Upskill team members in high-demand AI/ML technologies

#### Technology Evolution Path
**Post-MVP Considerations**:
- **Performance Optimisation**: Evaluate Go/Rust for high-throughput components
- **Microservices Architecture**: Split into specialised services for better scalability
- **Container Orchestration**: Kubernetes deployment for enterprise reliability
- **Multi-Model Support**: Framework to easily swap or ensemble different AI models
- **Edge Processing**: Consider local processing for latency-critical scenarios

## Future Roadmap

### MVP Phase (3-6 months)
**Core Splunk Integration:**
- Implement core SPL queries for top 5 critical services
- Deploy basic Python parsing and Gemini integration
- Create initial dashboard with manual validation workflow
- Establish feedback loop for model improvement

**Universal API Development:**
- **Log Analysis API**: Allow any application to submit logs for AI-powered analysis
- **Document Management API**: Pre-save application documentation by app_id
- **Simple Caching System**: Hash-based response caching (app_id + error_hash + document_hash)
- **Authentication & Rate Limiting**: Secure API access with per-application quotas

### Post-MVP Enhancements (6-12 months)
- Expand Splunk coverage to all monitored services
- Implement automated root cause analysis improvements
- Add predictive failure detection capabilities
- **Enhanced Vector-Based Caching**: Semantic similarity search with embeddings (v1.5 feature)
- **Advanced Analytics Dashboard**: API usage metrics and caching effectiveness

### Long Term (12+ months)
- Multi-cloud log source integration
- Advanced ML models for pattern prediction
- Automated remediation execution (with approval workflows)
- Integration with CI/CD pipelines for proactive issue prevention
- **Hybrid Caching Architecture**: Combined hash-based and vector similarity caching

## MVP API Architecture & Extended Capabilities

The MVP will include both Splunk integration and universal API capabilities to maximise platform value from day one.

### Universal Log Analysis API
**Objective**: Allow any application to submit logs and receive AI-powered analysis and resolution guidance alongside core Splunk functionality.

**Core API Endpoints**:
```python
# Submit logs for analysis
POST /api/v1/analyse-logs
{
    "app_id": "my-application",
    "logs": ["ERROR: Database connection failed", "FATAL: OutOfMemoryException"],
    "context": {
        "environment": "production",
        "version": "1.2.3",
        "timestamp": "2025-01-15T10:30:45Z"
    },
    "supporting_docs": ["runbook.md", "troubleshooting.pdf"]  # Optional
}

# Response
{
    "analysis_id": "ana_123456",
    "root_cause": "Database connection pool exhaustion",
    "confidence": 0.87,
    "resolution_steps": [...],
    "similar_incidents": [...],
    "estimated_resolution_time": "15 minutes"
}
```

### Document Management API
**Pre-save Application Documentation**:
```python
# Register application documentation
POST /api/v1/apps/{app_id}/documents
{
    "document_type": "runbook",
    "title": "Database Connection Issues",
    "content": "...",
    "tags": ["database", "connection", "troubleshooting"],
    "version": "1.0"
}

# List registered documents
GET /api/v1/apps/{app_id}/documents

# Update document
PUT /api/v1/apps/{app_id}/documents/{doc_id}
```

**Benefits**:
- **Reduced API Payload**: Avoid submitting large documents with each request
- **Version Control**: Track document changes and effectiveness over time
- **Centralised Knowledge**: Build comprehensive knowledge base per application
- **Access Control**: Secure document storage with app-level permissions

### Simple Response Caching (MVP Implementation)

#### Hash-Based Caching
```python
# Cache key generation
cache_key = f"{app_id}:{error_hash}:{document_hash}"

# Example implementation
def get_cache_key(app_id, logs, docs):
    error_signature = extract_error_signature(logs)
    doc_hash = hash_documents(docs)
    return f"{app_id}:{hash(error_signature)}:{doc_hash}"

# Cache lookup before AI inference
cached_response = redis.get(cache_key)
if cached_response:
    return json.loads(cached_response)
else:
    ai_response = call_gemini_analysis(logs, docs)
    redis.setex(cache_key, 3600, json.dumps(ai_response))  # 1 hour TTL
    return ai_response
```

### Technical Architecture for MVP APIs

#### API Gateway & Rate Limiting
```python
# Flask/FastAPI implementation
@app.route('/api/v1/analyse-logs', methods=['POST'])
@rate_limit("100 per hour")  # Per app_id
@authenticate_app_id
def analyse_logs():
    data = request.json
    app_id = data['app_id']
    
    # Cache lookup first
    cache_key = generate_cache_key(app_id, data['logs'], data.get('supporting_docs', []))
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return jsonify({**cached_result, "cached": True})
    
    # Get pre-registered documents
    app_docs = get_app_documents(app_id)
    
    # Combine with submitted docs
    all_docs = app_docs + data.get('supporting_docs', [])
    
    # AI analysis
    result = analyse_with_gemini(data['logs'], all_docs)
    
    # Cache result
    cache.setex(cache_key, 3600, json.dumps(result))
    
    return jsonify({**result, "cached": False})
```

#### Document Storage Integration
```python
# Splunk-based document storage
class DocumentManager:
    def store_document(self, app_id, doc_data):
        doc_entry = {
            "app_id": app_id,
            "document_id": generate_id(),
            "title": doc_data['title'],
            "content": doc_data['content'],
            "document_type": doc_data['type'],
            "tags": doc_data.get('tags', []),
            "version": doc_data.get('version', '1.0'),
            "created_at": datetime.utcnow().isoformat(),
            "content_hash": hashlib.sha256(doc_data['content'].encode()).hexdigest()
        }
        
        # Store in Splunk index
        self.splunk_client.index('app_documents').submit(json.dumps(doc_entry))
        
        return doc_entry['document_id']
    
    def get_app_documents(self, app_id):
        search_query = f'index=app_documents app_id="{app_id}" | table title, content, tags, version'
        return self.splunk_client.jobs.oneshot(search_query)
```

### MVP Performance & Scaling Considerations

**Caching Strategy Benefits**:
- **Cost Reduction**: Avoid duplicate AI inference calls for similar errors
- **Latency Improvement**: Instant responses for cached queries
- **Learning Acceleration**: Build knowledge base of successful resolutions
- **Resource Optimisation**: Reduce Gemini API usage and costs

**MVP Technical Stack**:
- **API Framework**: FastAPI for async performance
- **Document Storage**: Splunk indexes + file storage (S3/Azure Blob)
- **Cache Layer**: Redis for hash-based caching
- **Authentication**: JWT tokens with app_id validation
- **Rate Limiting**: Redis-based sliding window rate limiter

## Post-MVP: Vector-Based Semantic Caching

### Enhanced Caching with Semantic Similarity (v1.5)
```python
# Enhanced caching with semantic similarity
def semantic_cache_lookup(app_id, logs, docs):
    # Generate embedding for current error
    error_embedding = generate_embedding(extract_error_context(logs))
    
    # Search vector database for similar errors
    similar_errors = vector_db.search(
        vector=error_embedding,
        filter={"app_id": app_id},
        threshold=0.85  # Similarity threshold
    )
    
    if similar_errors:
        # Return cached response for most similar error
        return get_cached_response(similar_errors[0]['cache_key'])
    
    # No similar error found, generate new response
    ai_response = call_gemini_analysis(logs, docs)
    
    # Store in vector DB and cache
    cache_key = store_vector_cache(app_id, error_embedding, ai_response)
    return ai_response

# Vector database schema
{
    "id": "vec_123456",
    "app_id": "my-application",
    "error_embedding": [0.1, 0.2, ...],  # 768-dimensional vector
    "error_signature": "Database connection failed",
    "document_context": ["runbook_v1.0", "troubleshooting_v2.1
