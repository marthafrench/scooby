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

### Phase 3: Dashboard Integration
- Real-time incident classification
- Automated root cause analysis
- Suggested remediation steps
- Expert contact information
- Historical pattern analysis

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

#### Option 4: Alternative Programming Languages
**Considerations**:

| Language | Trade-offs |
|----------|------------|
| **Go** | Better performance, but limited AI/ML library ecosystem |
| **Java** | Enterprise-grade, but slower development for AI prototyping |
| **Node.js** | Fast development, but less mature AI/ML tooling |
| **Rust** | Excellent performance, but steep learning curve for team |

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

### Short Term (3-6 months)
- Implement core SPL queries for top 5 critical services
- Deploy basic Python parsing and Gemini integration
- Create initial dashboard with manual validation workflow
- Establish feedback loop for model improvement

### Medium Term (6-12 months)
- Expand coverage to all monitored services
- Implement automated root cause analysis
- Add predictive failure detection capabilities
- Integrate with existing ticketing systems (JIRA, ServiceNow)

### Long Term (12+ months)
- Multi-cloud log source integration
- Advanced ML models for pattern prediction
- Automated remediation execution (with approval workflows)
- Integration with CI/CD pipelines for proactive issue prevention

### Advanced Capabilities
- **Predictive Analytics**: Identify potential failures before they occur
- **Automated Remediation**: Execute approved fixes automatically
- **Cross-Service Correlation**: Identify cascading failure patterns
- **Performance Optimisation**: Suggest infrastructure improvements based on failure patterns

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| **AI Overreliance** | High | Medium | Human-in-the-loop workflows, mandatory validation for P0/P1 incidents, fallback procedures |
| **Inconsistent Logging** | High | High | Log quality scoring system, developer training programmes, standardised logging libraries |
| **P0/P1 Latency** | Critical | Low | Fast-path triage with minimal AI processing, rule-based immediate escalation |
| **AI Hallucinations** | Medium | Medium | Confidence scoring, reasoning chains, evidence linking to source logs |
| **API Rate Limits** | Medium | Medium | Tiered processing, intelligent batching, upgrade path to higher tiers |
| **Model Accuracy Drift** | Medium | Medium | Continuous monitoring, A/B testing, regular model validation, feedback loops |
| **Integration Failures** | High | Low | Circuit breakers, fallback to manual processes, comprehensive monitoring |
| **Security Vulnerabilities** | High | Low | Leverage existing Splunk security, API key rotation, audit logging |
| **Cost Overrun** | Medium | Medium | Usage monitoring, cost alerts, tier optimisation, batch processing efficiency |
| **User Adoption Resistance** | Medium | Medium | Gradual rollout, training programmes, success story sharing, user feedback integration |

### Risk Monitoring Framework
- **Weekly**: API usage and cost tracking
- **Monthly**: Accuracy metrics and user satisfaction surveys  
- **Quarterly**: Security reviews and model performance assessments
- **Incident-based**: Immediate review of any AI recommendation failures

## Salient Points & Success Factors

### Technical Considerations
- **Data Privacy**: Ensure log data handling complies with security policies
- **Performance**: Monitor AI processing times to maintain real-time capabilities
- **Accuracy Monitoring**: Implement feedback mechanisms to track and improve AI recommendations
- **Fallback Procedures**: Maintain manual processes for system failures

### Organisational Alignment
- **Stakeholder Buy-in**: Ensure support from both IT operations and development teams
- **Change Management**: Plan for gradual rollout with training and support
- **Success Metrics**: Establish clear KPIs and regular review cycles
- **Continuous Improvement**: Create processes for incorporating user feedback

## Getting Started

1. **Environment Setup**: Configure Python environment with PyTorch, LangChain, and Splunk SDK
2. **SPL Development**: Create and test log extraction queries
3. **AI Integration**: Set up Gemini API access and initial prompt templates
4. **Dashboard Creation**: Build basic Splunk dashboard for results visualisation
5. **Pilot Testing**: Deploy with limited scope for validation
6. **Iterative Improvement**: Gather feedback and refine system performance

## Success Measurement

**Primary KPIs**:
- **Mean Time to Resolution (MTTR)**: Target 50% reduction from current baseline
- **First-Line Ticket Volume**: Target 40-60% reduction through self-service resolution
- **Incident Classification Accuracy**: Target >90% correct severity and category assignment
- **Self-Service Resolution Rate**: Target 70% of P2+ incidents resolved without escalation

**Secondary Metrics**:
- **User Satisfaction**: Survey support teams and end users quarterly
- **System Accuracy**: Track correctness of AI recommendations with feedback loops
- **Adoption Rate**: Monitor usage of AI-generated insights and recommendation acceptance
- **Cost per Incident**: Measure total cost reduction including labour and downtime

This system represents a significant step toward intelligent operations, transforming reactive incident response into proactive, data-driven problem resolution.
