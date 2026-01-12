"""
Training Plan Export Service
Export training plans to various formats (PDF, iCal, CSV, JSON)
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from io import BytesIO
import json
import csv
import logging

logger = logging.getLogger(__name__)


class TrainingPlanExportService:
    """Service for exporting training plans to various formats."""
    
    def export_to_json(self, plan_data: Dict[str, Any]) -> bytes:
        """
        Export plan to JSON format.
        
        Args:
            plan_data: Plan data dictionary
            
        Returns:
            JSON bytes
        """
        json_str = json.dumps(plan_data, indent=2, ensure_ascii=False, default=str)
        return json_str.encode('utf-8')
    
    def export_to_csv(self, plan_data: Dict[str, Any]) -> bytes:
        """
        Export plan to CSV format.
        
        Args:
            plan_data: Plan data dictionary
            
        Returns:
            CSV bytes
        """
        output = BytesIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Week', 'Day', 'Type', 'Name', 'Distance (km)', 
            'Duration (min)', 'Pace (min/km)', 'HR Zones', 'Notes'
        ])
        
        # Write workouts
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 0)
            for workout in week.get('workouts', []):
                writer.writerow([
                    week_num,
                    workout.get('day', ''),
                    workout.get('type', ''),
                    workout.get('name', ''),
                    workout.get('distance_km', ''),
                    workout.get('duration_minutes', ''),
                    workout.get('pace_target_min_per_km', ''),
                    ','.join(map(str, workout.get('heart_rate_zones', []))),
                    workout.get('notes', ''),
                ])
        
        output.seek(0)
        return output.getvalue()
    
    def export_to_ical(self, plan_data: Dict[str, Any], start_date: datetime) -> bytes:
        """
        Export plan to iCal format for calendar apps.
        
        Args:
            plan_data: Plan data dictionary
            start_date: Plan start date
            
        Returns:
            iCal bytes
        """
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Training Plan//RunCoach AI//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
        ]
        
        # Calculate dates for each workout
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 1)
            week_start = start_date + timedelta(weeks=week_num - 1)
            
            for workout in week.get('workouts', []):
                day_num = workout.get('day', 1)
                workout_date = week_start + timedelta(days=(day_num - 1) % 7)
                
                # Format date for iCal (YYYYMMDDTHHMMSSZ)
                dt_start = workout_date.strftime('%Y%m%dT000000Z')
                dt_end = (workout_date + timedelta(hours=1)).strftime('%Y%m%dT010000Z')
                
                # Create event
                summary = workout.get('name', workout.get('type', 'Training'))
                description_parts = []
                if workout.get('distance_km'):
                    description_parts.append(f"Distance: {workout['distance_km']} km")
                if workout.get('duration_minutes'):
                    description_parts.append(f"Duration: {workout['duration_minutes']} min")
                if workout.get('pace_target_min_per_km'):
                    description_parts.append(f"Pace: {workout['pace_target_min_per_km']} min/km")
                if workout.get('notes'):
                    description_parts.append(f"Notes: {workout['notes']}")
                
                description = '\\n'.join(description_parts)
                
                lines.extend([
                    'BEGIN:VEVENT',
                    f'UID:{plan_data.get("plan_id", "unknown")}-week{week_num}-day{day_num}@runcoach.ai',
                    f'DTSTART:{dt_start}',
                    f'DTEND:{dt_end}',
                    f'SUMMARY:{summary}',
                    f'DESCRIPTION:{description}',
                    'STATUS:CONFIRMED',
                    'END:VEVENT',
                ])
        
        lines.append('END:VCALENDAR')
        
        ical_content = '\r\n'.join(lines)
        return ical_content.encode('utf-8')
    
    def export_to_pdf(self, plan_data: Dict[str, Any]) -> bytes:
        """
        Export plan to PDF format.
        
        Note: This is a basic implementation. For production, consider using reportlab or similar.
        
        Args:
            plan_data: Plan data dictionary
            
        Returns:
            PDF bytes (simple text-based PDF for now)
        """
        # For a proper PDF, we'd use reportlab or similar
        # For now, return a simple text representation
        # In production, this should be replaced with proper PDF generation
        
        try:
            # Try to import reportlab if available
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(f"<b>{plan_data.get('plan_name', 'Training Plan')}</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Plan info
            info_text = f"""
            <b>Goal:</b> {plan_data.get('goal_type', 'N/A')}<br/>
            <b>Start Date:</b> {plan_data.get('start_date', 'N/A')}<br/>
            <b>Duration:</b> {plan_data.get('total_weeks', 0)} weeks<br/>
            """
            info = Paragraph(info_text, styles['Normal'])
            story.append(info)
            story.append(Spacer(1, 20))
            
            # Workouts table
            data = [['Week', 'Day', 'Type', 'Name', 'Distance (km)', 'Duration (min)']]
            
            for week in plan_data.get('weeks', []):
                week_num = week.get('week', 0)
                for workout in week.get('workouts', []):
                    data.append([
                        str(week_num),
                        str(workout.get('day', '')),
                        workout.get('type', ''),
                        workout.get('name', ''),
                        str(workout.get('distance_km', '')),
                        str(workout.get('duration_minutes', '')),
                    ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(table)
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except ImportError:
            # Fallback: return a simple text representation
            logger.warning("reportlab not available, using text fallback for PDF export")
            text_content = self._plan_to_text(plan_data)
            return text_content.encode('utf-8')
    
    def _plan_to_text(self, plan_data: Dict[str, Any]) -> str:
        """Convert plan to simple text format."""
        lines = [
            f"TRAINING PLAN: {plan_data.get('plan_name', 'Untitled')}",
            "=" * 60,
            f"Goal: {plan_data.get('goal_type', 'N/A')}",
            f"Start Date: {plan_data.get('start_date', 'N/A')}",
            f"Duration: {plan_data.get('total_weeks', 0)} weeks",
            "",
        ]
        
        for week in plan_data.get('weeks', []):
            lines.append(f"\nWeek {week.get('week', 0)}")
            lines.append("-" * 60)
            for workout in week.get('workouts', []):
                lines.append(f"  Day {workout.get('day', '')}: {workout.get('name', workout.get('type', ''))}")
                if workout.get('distance_km'):
                    lines.append(f"    Distance: {workout['distance_km']} km")
                if workout.get('duration_minutes'):
                    lines.append(f"    Duration: {workout['duration_minutes']} min")
        
        return '\n'.join(lines)


# Singleton instance
_export_service_instance: Optional[TrainingPlanExportService] = None

def get_export_service() -> TrainingPlanExportService:
    """Get or create the export service singleton."""
    global _export_service_instance
    if _export_service_instance is None:
        _export_service_instance = TrainingPlanExportService()
    return _export_service_instance
