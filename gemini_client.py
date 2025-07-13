import google.generativeai as genai
from typing import List, Dict, Any
import structlog
import json
from datetime import datetime

logger = structlog.get_logger()


class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info("Initialized Gemini client", model=settings.GEMINI_MODEL)

    def analyze_incident(self, incident: Incident, context_docs: str = "") -> AIAnalysis:
        """Analyze incident using Gemini 2.0 Flash"""

        prompt = self._build_analysis_prompt(incident, context_docs)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.GEMINI_MAX_TOKENS,
                )
            )

            # Parse the structured response
            analysis_data = self._parse_gemini_response(response.text, incident.id)
            return AIAnalysis(**analysis_data)

        except Exception as e:
            logger.error("Error analyzing incident with Gemini", incident_id=incident.id, error=str(e))
            return self._create_fallback_analysis(incident)

    def _build_analysis_prompt(self, incident: Incident, context_docs: str) -> str:
        log_text = "\n".join([f"[{entry.level}] {entry.message}" for entry in incident.log_entries[:10]])

        return f"""
You are an expert Site Reliability Engineer analyzing a system incident. Provide a detailed analysis in JSON format.

INCIDENT DETAILS:
- ID: {incident.id}
- Service: {incident.service}
- Severity: {incident.severity}
- Description: {incident.description}
- Timestamp: {incident.timestamp}

LOG ENTRIES:
{log_text}

CONTEXT DOCUMENTATION:
{context_docs}

Please analyze this incident and respond with a JSON object containing:
{{
    "confidence": <0-100 confidence score>,
    "severity_assessment": "<HIGH|MEDIUM|LOW>",
    "root_cause": "<detailed root cause analysis>",
    "recommendations": ["<actionable step 1>", "<actionable step 2>", ...],
    "business_impact": "<executive summary of business impact>",
    "escalation_path": "<escalation path and team contacts>",
    "reasoning_chain": ["<step 1 of analysis>", "<step 2 of analysis>", ...]
}}

Focus on:
1. Technical accuracy and actionable recommendations
2. Business impact in non-technical terms
3. Clear escalation paths
4. Evidence-based reasoning from the logs
5. Confidence scoring based on log quality and pattern recognition

Provide confidence scores based on:
- 90-100%: Clear patterns, high log quality, known solutions
- 70-89%: Good patterns, some ambiguity, likely solutions
- 50-69%: Unclear patterns, requires human validation
- Below 50%: Insufficient data, immediate escalation needed
"""

    def _parse_gemini_response(self, response_text: str, incident_id: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response into analysis data"""
        try:
            # Extract JSON from response (handle potential markdown formatting)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_text = response_text[json_start:json_end]

            analysis_data = json.loads(json_text)

            # Add required fields and defaults
            analysis_data.update({
                "incident_id": incident_id,
                "similar_incidents": self._find_similar_incidents(incident_id),
                "created_at": datetime.utcnow()
            })

            return analysis_data

        except Exception as e:
            logger.error("Failed to parse Gemini response", error=str(e), response=response_text[:200])
            return self._create_fallback_analysis_data(incident_id)

    def _find_similar_incidents(self, incident_id: str) -> List[Dict[str, Any]]:
        """Mock similar incident finder - would integrate with vector search in production"""
        return [
            {
                "id": "INC-2024-156",
                "similarity_score": 0.85,
                "resolution": "Increased connection pool size",
                "mttr": "15min",
                "resolution_date": datetime.utcnow()
            }
        ]

    def _create_fallback_analysis(self, incident: Incident) -> AIAnalysis:
        """Create fallback analysis when Gemini fails"""
        return AIAnalysis(
            incident_id=incident.id,
            confidence=30.0,
            severity_assessment="UNKNOWN",
            root_cause="Analysis failed - requires manual investigation",
            recommendations=["Escalate to on-call engineer", "Review logs manually"],
            business_impact="Impact assessment pending manual review",
            escalation_path="Immediate escalation to senior engineer",
            similar_incidents=[],
            reasoning_chain=["AI analysis unavailable", "Fallback to manual process"]
        )

    def _create_fallback_analysis_data(self, incident_id: str) -> Dict[str, Any]:
        """Create fallback analysis data dictionary"""
        return {
            "incident_id": incident_id,
            "confidence": 30.0,
            "severity_assessment": "UNKNOWN",
            "root_cause": "Analysis parsing failed - requires manual investigation",
            "recommendations": ["Escalate to on-call engineer", "Review logs manually"],
            "business_impact": "Impact assessment pending manual review",
            "escalation_path": "Immediate escalation to senior engineer",
            "similar_incidents": [],
            "reasoning_chain": ["AI response parsing failed", "Fallback to manual process"],
            "created_at": datetime.utcnow()
        }