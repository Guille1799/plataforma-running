"""
File Upload Service
Handles manual FIT, GPX, and TCX file uploads
Parses multiple formats and extracts workout data
Auto-converts GPX to FIT for enhanced compatibility
"""
import os
import tempfile
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

from fitparse import FitFile
from sqlalchemy.orm import Session

from .. import models
from .gpx_to_fit_converter import gpx_to_fit_converter


class FileUploadService:
    """Service for manual workout file uploads."""
    
    SUPPORTED_FORMATS = [".fit", ".gpx", ".tcx"]
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def is_supported(self, filename: str) -> bool:
        """Check if file format is supported."""
        ext = Path(filename).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def parse_fit_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse FIT file and extract workout data.
        
        Args:
            file_path: Path to FIT file
            
        Returns:
            Dictionary with workout metrics
        """
        fitfile = FitFile(file_path)
        
        data = {
            "sport_type": "running",
            "start_time": None,
            "duration_seconds": 0,
            "distance_meters": 0.0,
            "avg_heart_rate": None,
            "max_heart_rate": None,
            "calories": None,
            "elevation_gain": None,
            "avg_cadence": None,
            "max_cadence": None,
            "avg_stance_time": None,
            "avg_vertical_oscillation": None,
            "avg_leg_spring_stiffness": None,
            "left_right_balance": None
        }
        
        # Parse session records
        for record in fitfile.get_messages('session'):
            for field in record:
                if field.name == 'start_time':
                    data['start_time'] = field.value
                elif field.name == 'total_elapsed_time':
                    data['duration_seconds'] = int(field.value)
                elif field.name == 'total_distance':
                    data['distance_meters'] = float(field.value)
                elif field.name == 'avg_heart_rate':
                    data['avg_heart_rate'] = int(field.value)
                elif field.name == 'max_heart_rate':
                    data['max_heart_rate'] = int(field.value)
                elif field.name == 'total_calories':
                    data['calories'] = int(field.value)
                elif field.name == 'total_ascent':
                    data['elevation_gain'] = float(field.value)
                elif field.name == 'avg_cadence':
                    data['avg_cadence'] = float(field.value)
                elif field.name == 'max_cadence':
                    data['max_cadence'] = float(field.value)
                elif field.name == 'avg_stance_time':
                    data['avg_stance_time'] = float(field.value)
                elif field.name == 'avg_vertical_oscillation':
                    data['avg_vertical_oscillation'] = float(field.value)
                elif field.name == 'avg_stance_time_balance':
                    data['left_right_balance'] = float(field.value)
                elif field.name == 'sport':
                    sport = str(field.value).lower()
                    if 'running' in sport or 'run' in sport:
                        data['sport_type'] = 'running'
                    elif 'cycling' in sport or 'bike' in sport:
                        data['sport_type'] = 'cycling'
        
        # Calculate pace if we have distance and time
        if data['distance_meters'] > 0 and data['duration_seconds'] > 0:
            km = data['distance_meters'] / 1000
            minutes = data['duration_seconds'] / 60
            data['avg_pace'] = minutes / km if km > 0 else None
        
        # Set source metadata for FIT files
        data['source_type'] = 'garmin_fit'
        data['data_quality'] = 'high'  # FIT files have complete data
        
        return data
    
    def parse_gpx_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse GPX file and extract workout data.
        
        Args:
            file_path: Path to GPX file
            
        Returns:
            Dictionary with workout metrics
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle namespace
        ns = {
            'gpx': 'http://www.topografix.com/GPX/1/1',
            'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
        }
        if not root.tag.endswith('gpx'):
            # Try without namespace
            ns = {}
        
        data = {
            "sport_type": "running",
            "start_time": None,
            "duration_seconds": 0,
            "distance_meters": 0.0,
            "avg_heart_rate": None,
            "max_heart_rate": None,
            "elevation_gain": 0.0
        }
        
        # Find track points
        trkpts = root.findall('.//gpx:trkpt', ns) or root.findall('.//trkpt')
        
        if not trkpts:
            raise ValueError("No track points found in GPX file")
        
        # Extract start time (try with and without namespace)
        first_time = trkpts[0].find('gpx:time', ns)
        if first_time is None:
            first_time = trkpts[0].find('time')
        
        if first_time is not None:
            data['start_time'] = datetime.fromisoformat(
                first_time.text.replace('Z', '+00:00')
            )
        
        # Calculate duration
        last_time = trkpts[-1].find('gpx:time', ns)
        if last_time is None:
            last_time = trkpts[-1].find('time')
            
        if first_time is not None and last_time is not None:
            start = datetime.fromisoformat(first_time.text.replace('Z', '+00:00'))
            end = datetime.fromisoformat(last_time.text.replace('Z', '+00:00'))
            data['duration_seconds'] = int((end - start).total_seconds())
        
        # Calculate distance, elevation, and collect comprehensive metrics
        prev_lat = prev_lon = prev_ele = None
        prev_time = None
        total_distance = 0.0
        total_ascent = 0.0
        hr_values = []
        speed_values = []
        cadence_values = []
        elevation_values = []
        
        for trkpt in trkpts:
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            
            # Time (try with and without namespace)
            time_elem = trkpt.find('gpx:time', ns)
            if time_elem is None:
                time_elem = trkpt.find('time')
            
            current_time = None
            if time_elem is not None:
                current_time = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00'))
            
            # Elevation (try with and without namespace)
            ele_elem = trkpt.find('gpx:ele', ns)
            if ele_elem is None:
                ele_elem = trkpt.find('ele')
                
            ele = float(ele_elem.text) if ele_elem is not None else None
            if ele is not None:
                elevation_values.append(ele)
            
            # Heart rate (multiple possible extension paths for compatibility)
            hr_elem = trkpt.find('.//gpxtpx:hr', ns)
            if hr_elem is None:
                hr_elem = trkpt.find('.//gpx:hr', ns)
            if hr_elem is None:
                hr_elem = trkpt.find('.//hr')
            
            if hr_elem is not None:
                try:
                    hr_values.append(int(hr_elem.text))
                except (ValueError, TypeError):
                    pass
            
            # Cadence (if available in extensions)
            cad_elem = trkpt.find('.//gpxtpx:cad', ns)
            if cad_elem is None:
                cad_elem = trkpt.find('.//cad')
            if cad_elem is None:
                cad_elem = trkpt.find('.//cadence')
                
            if cad_elem is not None:
                try:
                    cadence_values.append(int(cad_elem.text))
                except (ValueError, TypeError):
                    pass
            
            # Calculate distance using Haversine formula
            if prev_lat is not None and prev_lon is not None:
                from math import radians, sin, cos, sqrt, atan2
                
                R = 6371000  # Earth radius in meters
                lat1, lon1 = radians(prev_lat), radians(prev_lon)
                lat2, lon2 = radians(lat), radians(lon)
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                distance = R * c
                
                total_distance += distance
                
                # Calculate speed (m/s) if we have timestamps
                if current_time and prev_time:
                    time_delta = (current_time - prev_time).total_seconds()
                    if time_delta > 0:
                        speed = distance / time_delta
                        speed_values.append(speed)
            
            # Calculate elevation gain
            if prev_ele is not None and ele is not None and ele > prev_ele:
                total_ascent += (ele - prev_ele)
            
            prev_lat, prev_lon, prev_ele = lat, lon, ele
            prev_time = current_time
        
        data['distance_meters'] = total_distance
        data['elevation_gain'] = total_ascent
        
        # Heart rate stats
        if hr_values:
            data['avg_heart_rate'] = int(sum(hr_values) / len(hr_values))
            data['max_heart_rate'] = max(hr_values)
            data['min_heart_rate'] = min(hr_values)
        
        # Speed and pace stats
        if speed_values:
            avg_speed_ms = sum(speed_values) / len(speed_values)
            data['avg_speed_ms'] = avg_speed_ms
            data['max_speed_ms'] = max(speed_values)
            
            # Calculate pace (min/km)
            if avg_speed_ms > 0:
                pace_sec_per_km = 1000 / avg_speed_ms
                minutes = int(pace_sec_per_km // 60)
                seconds = int(pace_sec_per_km % 60)
                data['avg_pace_min_km'] = f"{minutes}:{seconds:02d}"
        
        # Cadence stats
        if cadence_values:
            data['avg_cadence'] = int(sum(cadence_values) / len(cadence_values))
            data['max_cadence'] = max(cadence_values)
        
        # Elevation stats
        if elevation_values:
            data['min_altitude'] = min(elevation_values)
            data['max_altitude'] = max(elevation_values)
        
        # Estimate calories (rough formula: 0.75 * weight * distance_km)
        # Use 75kg as default weight
        if total_distance > 0:
            data['calories'] = int(0.75 * 75 * (total_distance / 1000))
        
        # Set source metadata for GPX files
        data['source_type'] = 'gpx_upload'
        # Determine data quality based on available metrics
        if hr_values and cadence_values:
            data['data_quality'] = 'high'
        elif hr_values:
            data['data_quality'] = 'medium'
        else:
            data['data_quality'] = 'basic'
        
        return data
    
    def parse_tcx_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse TCX file and extract workout data.
        
        Args:
            file_path: Path to TCX file
            
        Returns:
            Dictionary with workout metrics
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle namespace
        ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
        
        data = {
            "sport_type": "running",
            "start_time": None,
            "duration_seconds": 0,
            "distance_meters": 0.0,
            "avg_heart_rate": None,
            "max_heart_rate": None,
            "calories": None
        }
        
        # Find activity
        activity = root.find('.//tcx:Activity', ns)
        if activity is None:
            raise ValueError("No activity found in TCX file")
        
        # Sport type
        sport = activity.get('Sport', 'Running').lower()
        if 'run' in sport:
            data['sport_type'] = 'running'
        elif 'bik' in sport or 'cycl' in sport:
            data['sport_type'] = 'cycling'
        
        # Find lap (summary data)
        lap = activity.find('.//tcx:Lap', ns)
        if lap:
            # Start time
            start_time = lap.get('StartTime')
            if start_time:
                data['start_time'] = datetime.fromisoformat(
                    start_time.replace('Z', '+00:00')
                )
            
            # Duration
            total_time = lap.find('tcx:TotalTimeSeconds', ns)
            if total_time is not None:
                data['duration_seconds'] = int(float(total_time.text))
            
            # Distance
            distance = lap.find('tcx:DistanceMeters', ns)
            if distance is not None:
                data['distance_meters'] = float(distance.text)
            
            # Calories
            calories = lap.find('tcx:Calories', ns)
            if calories is not None:
                data['calories'] = int(calories.text)
            
            # Heart rate
            avg_hr = lap.find('.//tcx:AverageHeartRateBpm/tcx:Value', ns)
            if avg_hr is not None:
                data['avg_heart_rate'] = int(avg_hr.text)
            
            max_hr = lap.find('.//tcx:MaximumHeartRateBpm/tcx:Value', ns)
            if max_hr is not None:
                data['max_heart_rate'] = int(max_hr.text)
        
        # Calculate pace
        if data['distance_meters'] > 0 and data['duration_seconds'] > 0:
            km = data['distance_meters'] / 1000
            minutes = data['duration_seconds'] / 60
            data['avg_pace'] = minutes / km if km > 0 else None
        
        return data
    
    def parse_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Parse workout file based on extension.
        
        Auto-converts GPX to FIT for better data extraction.
        
        Args:
            file_path: Path to file
            filename: Original filename
            
        Returns:
            Parsed workout data
        """
        ext = Path(filename).suffix.lower()
        
        if ext == '.fit':
            return self.parse_fit_file(file_path)
        elif ext == '.gpx':
            # Direct GPX parsing with enhanced metrics extraction
            return self.parse_gpx_file(file_path)
        elif ext == '.tcx':
            return self.parse_tcx_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def create_workout_from_file(
        self,
        db: Session,
        user_id: int,
        file_path: str,
        filename: str
    ) -> models.Workout:
        """
        Parse file and create workout in database.
        
        Args:
            db: Database session
            user_id: User ID
            file_path: Path to uploaded file
            filename: Original filename
            
        Returns:
            Created workout
        """
        # Parse file
        data = self.parse_file(file_path, filename)
        
        # Create workout
        workout = models.Workout(
            user_id=user_id,
            sport_type=data.get('sport_type', 'running'),
            start_time=data.get('start_time') or datetime.utcnow(),
            duration_seconds=data.get('duration_seconds', 0),
            distance_meters=data.get('distance_meters', 0.0),
            avg_heart_rate=data.get('avg_heart_rate'),
            max_heart_rate=data.get('max_heart_rate'),
            avg_pace=data.get('avg_pace'),
            max_speed=data.get('max_speed'),
            calories=data.get('calories'),
            elevation_gain=data.get('elevation_gain'),
            avg_cadence=data.get('avg_cadence'),
            max_cadence=data.get('max_cadence'),
            avg_stance_time=data.get('avg_stance_time'),
            avg_vertical_oscillation=data.get('avg_vertical_oscillation'),
            avg_leg_spring_stiffness=data.get('avg_leg_spring_stiffness'),
            left_right_balance=data.get('left_right_balance'),
            file_name=filename,
            created_at=datetime.utcnow()
        )
        
        db.add(workout)
        db.commit()
        db.refresh(workout)
        
        print(f"[UPLOAD] Created workout from {filename}")
        return workout


# Singleton instance
file_upload_service = FileUploadService()
