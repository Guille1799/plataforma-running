"""
Apple Health Integration Service
Handles Apple Health export.xml parsing for iPhone users
"""
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from .. import models


class AppleHealthService:
    """Service for parsing Apple Health export data."""
    
    def parse_export_xml(self, xml_content: str) -> Dict[date, Dict[str, Any]]:
        """
        Parse Apple Health export.xml file.
        
        Args:
            xml_content: Content of export.xml file
            
        Returns:
            Dict mapping dates to health metrics
        """
        print("[APPLE HEALTH] Parsing export.xml...")
        
        root = ET.fromstring(xml_content)
        
        # Dictionary to accumulate metrics by date
        metrics_by_date: Dict[date, Dict[str, Any]] = {}
        
        # Parse all records
        for record in root.findall(".//Record"):
            record_type = record.get("type")
            
            # Skip if not a health metric we care about
            if not record_type:
                continue
            
            # Parse date
            start_date_str = record.get("startDate")
            if not start_date_str:
                continue
            
            try:
                record_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
            except:
                continue
            
            # Initialize date entry
            if record_date not in metrics_by_date:
                metrics_by_date[record_date] = {
                    "resting_hr_values": [],
                    "hrv_values": [],
                    "sleep_durations": [],
                    "steps_values": [],
                    "calories_values": []
                }
            
            metrics = metrics_by_date[record_date]
            
            # Extract value
            value_str = record.get("value")
            if not value_str:
                continue
            
            try:
                value = float(value_str)
            except:
                continue
            
            # Map record types to our metrics
            if record_type == "HKQuantityTypeIdentifierRestingHeartRate":
                metrics["resting_hr_values"].append(value)
            
            elif record_type == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN":
                metrics["hrv_values"].append(value)
            
            elif record_type == "HKQuantityTypeIdentifierStepCount":
                metrics["steps_values"].append(value)
            
            elif record_type == "HKQuantityTypeIdentifierActiveEnergyBurned":
                metrics["calories_values"].append(value)
        
        # Parse sleep data from HKCategoryTypeIdentifierSleepAnalysis
        for record in root.findall(".//Record[@type='HKCategoryTypeIdentifierSleepAnalysis']"):
            start_date_str = record.get("startDate")
            end_date_str = record.get("endDate")
            
            if not start_date_str or not end_date_str:
                continue
            
            try:
                start_time = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                duration_minutes = (end_time - start_time).total_seconds() / 60
                
                # Sleep is attributed to the date it ends
                sleep_date = end_time.date()
                
                if sleep_date not in metrics_by_date:
                    metrics_by_date[sleep_date] = {"sleep_durations": []}
                
                if "sleep_durations" not in metrics_by_date[sleep_date]:
                    metrics_by_date[sleep_date]["sleep_durations"] = []
                
                metrics_by_date[sleep_date]["sleep_durations"].append(duration_minutes)
            except:
                continue
        
        # Aggregate daily metrics
        daily_metrics = {}
        
        for record_date, raw_metrics in metrics_by_date.items():
            aggregated = {}
            
            # Resting HR (average of the day)
            if raw_metrics.get("resting_hr_values"):
                aggregated["resting_hr_bpm"] = int(sum(raw_metrics["resting_hr_values"]) / len(raw_metrics["resting_hr_values"]))
            
            # HRV (average)
            if raw_metrics.get("hrv_values"):
                aggregated["hrv_ms"] = round(sum(raw_metrics["hrv_values"]) / len(raw_metrics["hrv_values"]), 1)
            
            # Sleep (total duration)
            if raw_metrics.get("sleep_durations"):
                aggregated["sleep_duration_minutes"] = int(sum(raw_metrics["sleep_durations"]))
            
            # Steps (total)
            if raw_metrics.get("steps_values"):
                aggregated["steps"] = int(sum(raw_metrics["steps_values"]))
            
            # Calories (total active calories)
            if raw_metrics.get("calories_values"):
                aggregated["active_calories"] = int(sum(raw_metrics["calories_values"]))
            
            if aggregated:
                daily_metrics[record_date] = aggregated
        
        print(f"[APPLE HEALTH] Parsed {len(daily_metrics)} days of health data")
        
        return daily_metrics
    
    def import_health_metrics(
        self,
        db: Session,
        user_id: int,
        xml_content: str,
        max_days: int = 30
    ) -> List[models.HealthMetric]:
        """
        Import health metrics from Apple Health export.
        
        Args:
            db: Database session
            user_id: User ID
            xml_content: Content of export.xml
            max_days: Maximum days to import (default 30)
            
        Returns:
            List of imported HealthMetric objects
        """
        # Parse XML
        daily_metrics = self.parse_export_xml(xml_content)
        
        # Filter to recent dates only
        cutoff_date = date.today() - timedelta(days=max_days)
        recent_metrics = {
            d: m for d, m in daily_metrics.items()
            if d >= cutoff_date
        }
        
        imported_metrics = []
        
        for metric_date, data in recent_metrics.items():
            # Check if already exists
            existing = db.query(models.HealthMetric).filter(
                models.HealthMetric.user_id == user_id,
                models.HealthMetric.date == metric_date,
                models.HealthMetric.source == "apple_health"
            ).first()
            
            if existing:
                # Update existing
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.data_quality = self._determine_quality(data)
                imported_metrics.append(existing)
                print(f"[APPLE HEALTH] Updated {metric_date}")
            else:
                # Create new
                metric = models.HealthMetric(
                    user_id=user_id,
                    date=metric_date,
                    source="apple_health",
                    data_quality=self._determine_quality(data),
                    **data
                )
                db.add(metric)
                imported_metrics.append(metric)
                print(f"[APPLE HEALTH] Imported {metric_date}")
        
        db.commit()
        
        # Update user's last sync
        user = db.query(models.User).get(user_id)
        if user:
            user.last_apple_health_sync = datetime.utcnow()
            db.commit()
        
        print(f"[APPLE HEALTH] Imported {len(imported_metrics)} days")
        
        return imported_metrics
    
    def _determine_quality(self, data: Dict[str, Any]) -> str:
        """Determine data quality based on available metrics."""
        has_hrv = "hrv_ms" in data
        has_sleep = "sleep_duration_minutes" in data
        has_hr = "resting_hr_bpm" in data
        
        if has_hrv and has_sleep and has_hr:
            return "high"
        elif has_sleep or has_hr:
            return "medium"
        else:
            return "basic"


# Singleton instance
apple_health_service = AppleHealthService()
