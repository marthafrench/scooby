from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import structlog
from contextlib import asynccontextmanager
import uvicorn

from cache_manager import CacheManager
from config import settings
from gemini_client import GeminiClient
from rate_limiter import RateLimiter
from splunk_client import SplunkClient

# Initialize components
cache_manager = CacheManager()
rate_limiter = RateLimiter(cache_manager)
splunk_client = SplunkClient()
gemini_client = GeminiClient()

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Scooby AI Incident Response System")
    yield
    logger.info("Shutting down Scooby AI Incident Response System")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


async def verify_rate_limit(request_id: str = "anonymous"):
    """Rate limiting dependency"""
    if not rate_limiter.is_allowed(request_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )


@app.get("/")
async def root():
    return {"message": "Scooby AI Incident Response System", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        cache_manager.redis_client.ping()

        # Test Splunk connection (basic check)
        splunk_client.service.info()

        return {
            "status": "healthy",
            "components": {
                "redis": "connected",
                "splunk": "connected",
                "gemini": "configured"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get(f"{settings.API_V1_STR}/incidents", response_model=List[Incident])
async def get_incidents(
        hours: int = 24,
        severity: Optional[SeverityLevel] = None,
        _: None = Depends(verify_rate_limit)
):
    """Get recent incidents from Splunk"""
    try:
        incidents = splunk_client.get_recent_incidents(hours)

        if severity:
            incidents = [inc for inc in incidents if inc.severity == severity]

        logger.info("Retrieved incidents", count=len(incidents), hours=hours)
        return incidents

    except Exception as e:
        logger.error("Error retrieving incidents", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve incidents")


@app.post(f"{settings.API_V1_STR}/analyze", response_model=AIAnalysis)
async def analyze_incident_endpoint(
        request: AnalysisRequest,
        _: None = Depends(verify_rate_limit)
):
    """Analyze incident logs using AI"""
    try:
        # Generate hashes for caching
        log_hash = cache_manager.generate_content_hash(request.log_data)
        doc_hash = cache_manager.generate_content_hash(request.documentation or "")
        app_id = request.app_id or "default"

        # Check cache first
        cached_analysis = cache_manager.get_analysis_cache(app_id, log_hash, doc_hash)
        if cached_analysis:
            logger.info("Returning cached analysis", app_id=app_id)
            return cached_analysis

        # Create incident object from request
        incident = Incident(
            id=f"REQ-{int(time.time())}",
            service=request.service_name,
            severity=request.severity_hint or SeverityLevel.P3,
            status=IncidentStatus.ANALYZING,
            timestamp=datetime.utcnow(),
            description=f"Analysis request for {request.service_name}",
            log_entries=[
                LogEntry(
                    timestamp=datetime.utcnow(),
                    level=log.get('level', 'INFO'),
                    message=log.get('message', ''),
                    service=request.service_name,
                    metadata=log.get('metadata')
                ) for log in request.log_data
            ]
        )

        # Perform AI analysis
        analysis = gemini_client.analyze_incident(incident, request.documentation or "")

        # Cache the result
        cache_manager.set_analysis_cache(app_id, log_hash, doc_hash, analysis)

        logger.info("Generated new analysis", incident_id=incident.id, confidence=analysis.confidence)
        return analysis

    except Exception as e:
        logger.error("Error analyzing incident", error=str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.post(f"{settings.API_V1_STR}/feedback")
async def submit_feedback(
        feedback: FeedbackRequest,
        _: None = Depends(verify_rate_limit)
):
    """Submit feedback on AI analysis"""
    try:
        # Store feedback in Redis for analytics
        feedback_key = f"feedback:{feedback.incident_id}:{feedback.analysis_id}"
        feedback_data = {
            "incident_id": feedback.incident_id,
            "analysis_id": feedback.analysis_id,
            "is_correct": feedback.is_correct,
            "user_id": feedback.user_id,
            "comments": feedback.comments,
            "timestamp": datetime.utcnow().isoformat()
        }

        cache_manager.redis_client.setex(
            feedback_key,
            timedelta(days=30),  # Keep feedback for 30 days
            json.dumps(feedback_data)
        )

        logger.info("Feedback submitted",
                    incident_id=feedback.incident_id,
                    is_correct=feedback.is_correct,
                    user_id=feedback.user_id)

        return {"status": "success", "message": "Feedback recorded"}

    except Exception as e:
        logger.error("Error submitting feedback", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to record feedback")


@app.get(f"{settings.API_V1_STR}/analytics")
async def get_analytics(_: None = Depends(verify_rate_limit)):
    """Get system analytics and metrics"""
    try:
        # Get feedback statistics
        feedback_keys = cache_manager.redis_client.keys("feedback:*")
        total_feedback = len(feedback_keys)

        correct_count = 0
        if feedback_keys:
            for key in feedback_keys:
                feedback_data = json.loads(cache_manager.redis_client.get(key))
                if feedback_data.get('is_correct'):
                    correct_count += 1

        accuracy = (correct_count / total_feedback * 100) if total_feedback > 0 else 0

        # Mock additional metrics (would come from real data in production)
        analytics = {
            "total_incidents_analyzed": total_feedback + 50,  # Mock baseline
            "ai_accuracy_percentage": round(accuracy, 1),
            "average_response_time_seconds": 2.3,
            "cache_hit_rate_percentage": 35.2,
            "cost_savings_estimate": 24000,
            "active_users": 15,
            "feedback_stats": {
                "total_feedback": total_feedback,
                "correct_feedback": correct_count,
                "incorrect_feedback": total_feedback - correct_count
            }
        }

        return analytics

    except Exception as e:
        logger.error("Error retrieving analytics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )