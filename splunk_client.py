import splunklib.client as client
import splunklib.results as results
from typing import List, Dict, Any
import structlog
from datetime import datetime, timedelta
import json

logger = structlog.get_logger()


class SplunkClient:
    def __init__(self):
        self.service = client.connect(
            host=settings.SPLUNK_HOST,
            port=settings.SPLUNK_PORT,
            username=settings.SPLUNK_USERNAME,
            password=settings.SPLUNK_PASSWORD,
            scheme=settings.SPLUNK_SCHEME
        )
        logger.info("Connected to Splunk", host=settings.SPLUNK_HOST)

    def get_recent_incidents(self, hours: int = 24) -> List[Incident]:
        """Fetch recent incidents from Splunk logs"""
        query = f"""
        search index=main earliest=-{hours}h 
        | where match(_raw, "ERROR|FATAL|CRITICAL") 
        | eval severity=case(
            match(_raw, "FATAL|CRITICAL"), "P1",
            match(_raw, "ERROR"), "P2",
            1==1, "P3"
        )
        | stats count by host, source, severity, _time
        | sort -_time
        | head 50
        """

        try:
            job = self.service.jobs.create(query)

            # Wait for job completion
            while not job.is_done():
                pass

            incidents = []
            for result in results.ResultsReader(job.results()):
                if isinstance(result, dict):
                    incident = self._parse_incident_from_result(result)
                    if incident:
                        incidents.append(incident)

            logger.info("Fetched incidents from Splunk", count=len(incidents))
            return incidents

        except Exception as e:
            logger.error("Error fetching incidents from Splunk", error=str(e))
            return []

    def search_logs_for_incident(self, service: str, timeframe_hours: int = 1) -> List[LogEntry]:
        """Search for specific service logs"""
        query = f"""
        search index=main source="*{service}*" earliest=-{timeframe_hours}h
        | head 100
        | eval log_level=case(
            match(_raw, "ERROR"), "ERROR",
            match(_raw, "WARN"), "WARN",
            match(_raw, "INFO"), "INFO",
            1==1, "DEBUG"
        )
        """

        try:
            job = self.service.jobs.create(query)
            while not job.is_done():
                pass

            log_entries = []
            for result in results.ResultsReader(job.results()):
                if isinstance(result, dict):
                    log_entry = LogEntry(
                        timestamp=datetime.fromisoformat(result.get('_time', datetime.utcnow().isoformat())),
                        level=result.get('log_level', 'INFO'),
                        message=result.get('_raw', ''),
                        service=service,
                        metadata={"host": result.get('host'), "source": result.get('source')}
                    )
                    log_entries.append(log_entry)

            return log_entries

        except Exception as e:
            logger.error("Error searching logs", service=service, error=str(e))
            return []

    def _parse_incident_from_result(self, result: Dict) -> Optional[Incident]:
        """Parse Splunk result into Incident model"""
        try:
            return Incident(
                id=f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{result.get('host', 'unknown')[:3].upper()}",
                service=result.get('source', 'unknown-service'),
                severity=SeverityLevel(result.get('severity', 'P3')),
                status=IncidentStatus.ACTIVE,
                timestamp=datetime.fromisoformat(result.get('_time', datetime.utcnow().isoformat())),
                description=f"Issues detected in {result.get('source', 'service')}",
                log_entries=[],
                tags=["auto-detected"]
            )
        except Exception as e:
            logger.warning("Failed to parse incident", result=result, error=str(e))
            return None