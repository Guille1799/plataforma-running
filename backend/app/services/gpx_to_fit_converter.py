"""
GPX to FIT Converter Service

Converts GPX files (Xiaomi, Amazfit, etc.) to FIT format with full metrics.
Creates synthetic FIT files that are compatible with Garmin ecosystem.
"""
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime, timezone, timedelta
import gpxpy
import gpxpy.gpx
from io import BytesIO
import struct
import math


class GPXToFITConverter:
    """
    Converts GPX files to FIT format.
    
    FIT (Flexible and Interoperable Data Transfer) is the industry standard
    for fitness data. This converter creates valid FIT files from GPX input.
    """
    
    def __init__(self):
        # FIT file constants
        self.FIT_PROTOCOL_VERSION = 0x20  # 2.0
        self.FIT_PROFILE_VERSION = 2111   # 21.11
        
        # Message types
        self.MSG_FILE_ID = 0
        self.MSG_ACTIVITY = 34
        self.MSG_SESSION = 18
        self.MSG_LAP = 19
        self.MSG_RECORD = 20
        self.MSG_EVENT = 21
        
        # Field definitions
        self.FIELD_TIMESTAMP = 253
        self.FIELD_START_TIME = 2
        self.FIELD_TOTAL_ELAPSED_TIME = 7
        self.FIELD_TOTAL_TIMER_TIME = 8
        self.FIELD_TOTAL_DISTANCE = 9
        self.FIELD_TOTAL_CALORIES = 11
        self.FIELD_AVG_HEART_RATE = 16
        self.FIELD_MAX_HEART_RATE = 17
        self.FIELD_AVG_SPEED = 14
        self.FIELD_MAX_SPEED = 15
        self.FIELD_TOTAL_ASCENT = 22
        self.FIELD_SPORT = 5
        self.FIELD_EVENT = 0
        self.FIELD_EVENT_TYPE = 1
        
        # Record fields
        self.FIELD_POSITION_LAT = 0
        self.FIELD_POSITION_LONG = 1
        self.FIELD_ALTITUDE = 2
        self.FIELD_HEART_RATE = 3
        self.FIELD_CADENCE = 4
        self.FIELD_DISTANCE = 5
        self.FIELD_SPEED = 6
        
        # Sport type: running = 1
        self.SPORT_RUNNING = 1
        self.SPORT_CYCLING = 2
        self.SPORT_WALKING = 11
    
    def convert_gpx_to_fit(self, gpx_content: bytes) -> bytes:
        """
        Convert GPX content to FIT format.
        
        Args:
            gpx_content: Raw GPX file bytes
            
        Returns:
            FIT file as bytes
            
        Raises:
            ValueError: If GPX parsing fails
        """
        # Parse GPX
        gpx = gpxpy.parse(BytesIO(gpx_content))
        
        if not gpx.tracks:
            raise ValueError("GPX file contains no tracks")
        
        # Extract data from GPX
        track_data = self._extract_track_data(gpx)
        
        if not track_data["points"]:
            raise ValueError("GPX track contains no points")
        
        # Build FIT file
        fit_data = self._build_fit_file(track_data)
        
        return fit_data
    
    def _extract_track_data(self, gpx: gpxpy.gpx.GPX) -> Dict[str, Any]:
        """
        Extract all relevant data from GPX tracks.
        
        Args:
            gpx: Parsed GPX object
            
        Returns:
            Dictionary with track data
        """
        points = []
        total_distance = 0.0
        total_ascent = 0.0
        min_altitude = float('inf')
        max_altitude = float('-inf')
        heart_rates = []
        cadences = []
        speeds = []
        
        # Get first track (most GPX files have single track)
        track = gpx.tracks[0]
        
        # Determine sport type (heuristic based on speed)
        sport_type = self.SPORT_RUNNING  # Default
        
        for segment in track.segments:
            prev_point = None
            
            for point in segment.points:
                point_data = {
                    "lat": point.latitude,
                    "lon": point.longitude,
                    "elevation": point.elevation if point.elevation else 0.0,
                    "time": point.time,
                    "heart_rate": None,
                    "cadence": None,
                    "distance": total_distance,
                    "speed": None
                }
                
                # Extract HR and cadence from extensions (Zepp/Amazfit format)
                if point.extensions:
                    point_data["heart_rate"] = self._extract_extension_value(
                        point.extensions, ["hr", "heartrate", "HeartRate"]
                    )
                    point_data["cadence"] = self._extract_extension_value(
                        point.extensions, ["cadence", "Cadence", "cad"]
                    )
                
                # Calculate distance and speed
                if prev_point:
                    distance_delta = self._haversine_distance(
                        prev_point.latitude, prev_point.longitude,
                        point.latitude, point.longitude
                    )
                    total_distance += distance_delta
                    point_data["distance"] = total_distance
                    
                    # Calculate speed (m/s)
                    if point.time and prev_point.time:
                        time_delta = (point.time - prev_point.time).total_seconds()
                        if time_delta > 0:
                            point_data["speed"] = distance_delta / time_delta
                            speeds.append(point_data["speed"])
                    
                    # Calculate ascent
                    if point.elevation and prev_point.elevation:
                        elevation_delta = point.elevation - prev_point.elevation
                        if elevation_delta > 0:
                            total_ascent += elevation_delta
                
                # Track altitude range
                if point.elevation:
                    min_altitude = min(min_altitude, point.elevation)
                    max_altitude = max(max_altitude, point.elevation)
                
                # Collect metrics
                if point_data["heart_rate"]:
                    heart_rates.append(point_data["heart_rate"])
                if point_data["cadence"]:
                    cadences.append(point_data["cadence"])
                
                points.append(point_data)
                prev_point = point
        
        # Calculate summary statistics
        start_time = points[0]["time"]
        end_time = points[-1]["time"]
        total_time = (end_time - start_time).total_seconds()
        
        # Determine sport type based on average speed
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            # Running: 2-6 m/s (7.2-21.6 km/h)
            # Cycling: 5-15 m/s (18-54 km/h)
            if avg_speed > 8:
                sport_type = self.SPORT_CYCLING
            elif avg_speed < 2:
                sport_type = self.SPORT_WALKING
            else:
                sport_type = self.SPORT_RUNNING
        
        return {
            "points": points,
            "start_time": start_time,
            "total_time": total_time,
            "total_distance": total_distance,
            "total_ascent": total_ascent,
            "avg_heart_rate": int(sum(heart_rates) / len(heart_rates)) if heart_rates else None,
            "max_heart_rate": int(max(heart_rates)) if heart_rates else None,
            "avg_cadence": int(sum(cadences) / len(cadences)) if cadences else None,
            "max_cadence": int(max(cadences)) if cadences else None,
            "avg_speed": sum(speeds) / len(speeds) if speeds else None,
            "max_speed": max(speeds) if speeds else None,
            "min_altitude": min_altitude if min_altitude != float('inf') else None,
            "max_altitude": max_altitude if max_altitude != float('-inf') else None,
            "sport_type": sport_type
        }
    
    def _extract_extension_value(self, extensions: List, keys: List[str]) -> Optional[float]:
        """
        Extract numeric value from GPX extensions.
        
        Args:
            extensions: List of extension elements
            keys: Possible key names to search
            
        Returns:
            Numeric value or None
        """
        for ext in extensions:
            for key in keys:
                # Try different access patterns
                try:
                    # Direct attribute
                    if hasattr(ext, key):
                        value = getattr(ext, key)
                        if value is not None:
                            return float(value)
                    
                    # Dict-like access
                    if hasattr(ext, 'get') and ext.get(key):
                        return float(ext.get(key))
                    
                    # XML element search
                    if hasattr(ext, 'find'):
                        elem = ext.find(f".//{key}")
                        if elem is not None and elem.text:
                            return float(elem.text)
                    
                    # Namespace-aware search (Garmin extensions)
                    if hasattr(ext, 'findall'):
                        for ns_key in [
                            f"{{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}}{key}",
                            f"{{http://www.garmin.com/xmlschemas/GpxExtensions/v3}}{key}"
                        ]:
                            elem = ext.find(ns_key)
                            if elem is not None and elem.text:
                                return float(elem.text)
                except (ValueError, AttributeError):
                    continue
        
        return None
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _build_fit_file(self, track_data: Dict[str, Any]) -> bytes:
        """
        Build complete FIT file from track data.
        
        Creates a valid FIT file with:
        - File ID message
        - Activity message  
        - Session message
        - Lap message
        - Record messages (one per GPS point)
        - Event messages
        
        Args:
            track_data: Extracted track data
            
        Returns:
            Complete FIT file as bytes
        """
        buffer = BytesIO()
        
        # Write FIT header (14 bytes)
        self._write_fit_header(buffer, track_data)
        
        # Track data section start
        data_start = buffer.tell()
        
        # Write messages
        self._write_file_id_message(buffer, track_data)
        self._write_event_message(buffer, track_data, "start")
        
        # Write record messages (GPS points)
        for point in track_data["points"]:
            self._write_record_message(buffer, point)
        
        self._write_event_message(buffer, track_data, "stop")
        self._write_lap_message(buffer, track_data)
        self._write_session_message(buffer, track_data)
        self._write_activity_message(buffer, track_data)
        
        # Calculate CRC
        data_section = buffer.getvalue()[data_start:]
        crc = self._calculate_crc(data_section)
        buffer.write(struct.pack("<H", crc))
        
        # Update header with data size
        fit_data = buffer.getvalue()
        data_size = len(fit_data) - 14 - 2  # Exclude header and CRC
        
        # Rebuild with correct data size
        final_buffer = BytesIO()
        final_buffer.write(struct.pack("<BB", 14, self.FIT_PROTOCOL_VERSION))
        final_buffer.write(struct.pack("<H", self.FIT_PROFILE_VERSION))
        final_buffer.write(struct.pack("<I", data_size))
        final_buffer.write(b".FIT")
        final_buffer.write(struct.pack("<H", self._calculate_crc(final_buffer.getvalue())))
        final_buffer.write(fit_data[14:])
        
        return final_buffer.getvalue()
    
    def _write_fit_header(self, buffer: BinaryIO, track_data: Dict[str, Any]):
        """Write FIT file header (14 bytes)."""
        buffer.write(struct.pack("<BB", 14, self.FIT_PROTOCOL_VERSION))  # Header size, protocol
        buffer.write(struct.pack("<H", self.FIT_PROFILE_VERSION))  # Profile version
        buffer.write(struct.pack("<I", 0))  # Data size (placeholder)
        buffer.write(b".FIT")  # Data type
        buffer.write(struct.pack("<H", 0))  # CRC (placeholder)
    
    def _write_file_id_message(self, buffer: BinaryIO, track_data: Dict[str, Any]):
        """Write File ID message (defines file type and creation time)."""
        timestamp = self._datetime_to_fit_timestamp(track_data["start_time"])
        
        # Definition message
        buffer.write(struct.pack("<B", 0x40 | 0))  # Normal header, local msg 0
        buffer.write(struct.pack("<BBH", 0, 0, self.MSG_FILE_ID))  # Reserved, arch, msg num
        buffer.write(struct.pack("<B", 4))  # 4 fields
        
        # Field definitions: number, size, base type
        buffer.write(struct.pack("<BBB", 0, 1, 0))  # Type (enum)
        buffer.write(struct.pack("<BBB", 1, 2, 132))  # Manufacturer (uint16)
        buffer.write(struct.pack("<BBB", 2, 2, 132))  # Product (uint16)
        buffer.write(struct.pack("<BBB", 4, 4, 134))  # Time created (uint32)
        
        # Data message
        buffer.write(struct.pack("<B", 0))  # Local msg 0
        buffer.write(struct.pack("<B", 4))  # Type: activity
        buffer.write(struct.pack("<H", 1))  # Manufacturer: Garmin
        buffer.write(struct.pack("<H", 0))  # Product: generic
        buffer.write(struct.pack("<I", timestamp))  # Time created
    
    def _write_event_message(self, buffer: BinaryIO, track_data: Dict[str, Any], event_type: str):
        """Write Event message (start/stop markers)."""
        timestamp = self._datetime_to_fit_timestamp(
            track_data["start_time"] if event_type == "start" else 
            track_data["start_time"] + timedelta(seconds=track_data["total_time"])
        )
        
        # Definition message
        buffer.write(struct.pack("<B", 0x40 | 1))  # Normal header, local msg 1
        buffer.write(struct.pack("<BBH", 0, 0, self.MSG_EVENT))
        buffer.write(struct.pack("<B", 3))  # 3 fields
        
        buffer.write(struct.pack("<BBB", self.FIELD_TIMESTAMP, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_EVENT, 1, 0))
        buffer.write(struct.pack("<BBB", self.FIELD_EVENT_TYPE, 1, 0))
        
        # Data message
        buffer.write(struct.pack("<B", 1))
        buffer.write(struct.pack("<I", timestamp))
        buffer.write(struct.pack("<B", 0 if event_type == "start" else 9))  # timer/session
        buffer.write(struct.pack("<B", 0 if event_type == "start" else 1))  # start/stop
    
    def _write_record_message(self, buffer: BinaryIO, point: Dict[str, Any]):
        """Write Record message (GPS point with metrics)."""
        timestamp = self._datetime_to_fit_timestamp(point["time"])
        lat_semicircles = int(point["lat"] * (2**31 / 180))
        lon_semicircles = int(point["lon"] * (2**31 / 180))
        
        # Definition message (only write once per file, but simplified here)
        buffer.write(struct.pack("<B", 0x40 | 2))  # Normal header, local msg 2
        buffer.write(struct.pack("<BBH", 0, 0, self.MSG_RECORD))
        
        num_fields = 7  # Always include these base fields
        if point["heart_rate"]: num_fields += 1
        if point["cadence"]: num_fields += 1
        
        buffer.write(struct.pack("<B", num_fields))
        
        # Base fields
        buffer.write(struct.pack("<BBB", self.FIELD_TIMESTAMP, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_POSITION_LAT, 4, 133))
        buffer.write(struct.pack("<BBB", self.FIELD_POSITION_LONG, 4, 133))
        buffer.write(struct.pack("<BBB", self.FIELD_ALTITUDE, 2, 132))
        buffer.write(struct.pack("<BBB", self.FIELD_DISTANCE, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_SPEED, 2, 132))
        
        if point["heart_rate"]:
            buffer.write(struct.pack("<BBB", self.FIELD_HEART_RATE, 1, 2))
        if point["cadence"]:
            buffer.write(struct.pack("<BBB", self.FIELD_CADENCE, 1, 2))
        
        # Data message
        buffer.write(struct.pack("<B", 2))
        buffer.write(struct.pack("<I", timestamp))
        buffer.write(struct.pack("<i", lat_semicircles))
        buffer.write(struct.pack("<i", lon_semicircles))
        buffer.write(struct.pack("<H", int((point["elevation"] + 500) * 5)))  # Altitude with 0.2m resolution, 500m offset
        buffer.write(struct.pack("<I", int(point["distance"] * 100)))  # Distance in cm
        buffer.write(struct.pack("<H", int(point["speed"] * 1000) if point["speed"] else 0))  # Speed in mm/s
        
        if point["heart_rate"]:
            buffer.write(struct.pack("<B", int(point["heart_rate"])))
        if point["cadence"]:
            buffer.write(struct.pack("<B", int(point["cadence"])))
    
    def _write_lap_message(self, buffer: BinaryIO, track_data: Dict[str, Any]):
        """Write Lap message (summary of lap)."""
        # Simplified: one lap = entire activity
        self._write_summary_message(buffer, 3, self.MSG_LAP, track_data)
    
    def _write_session_message(self, buffer: BinaryIO, track_data: Dict[str, Any]):
        """Write Session message (summary of session)."""
        self._write_summary_message(buffer, 4, self.MSG_SESSION, track_data)
    
    def _write_activity_message(self, buffer: BinaryIO, track_data: Dict[str, Any]):
        """Write Activity message (top-level summary)."""
        timestamp = self._datetime_to_fit_timestamp(track_data["start_time"])
        total_timer_time = int(track_data["total_time"] * 1000)  # milliseconds
        num_sessions = 1
        
        # Definition
        buffer.write(struct.pack("<B", 0x40 | 5))
        buffer.write(struct.pack("<BBH", 0, 0, self.MSG_ACTIVITY))
        buffer.write(struct.pack("<B", 4))
        
        buffer.write(struct.pack("<BBB", self.FIELD_TIMESTAMP, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_TOTAL_TIMER_TIME, 4, 134))
        buffer.write(struct.pack("<BBB", 6, 2, 132))  # num_sessions
        buffer.write(struct.pack("<BBB", 1, 1, 0))  # type (manual)
        
        # Data
        buffer.write(struct.pack("<B", 5))
        buffer.write(struct.pack("<I", timestamp))
        buffer.write(struct.pack("<I", total_timer_time))
        buffer.write(struct.pack("<H", num_sessions))
        buffer.write(struct.pack("<B", 0))  # manual
    
    def _write_summary_message(self, buffer: BinaryIO, local_msg_num: int, msg_type: int, track_data: Dict[str, Any]):
        """Write summary message (lap or session)."""
        start_timestamp = self._datetime_to_fit_timestamp(track_data["start_time"])
        total_elapsed_time = int(track_data["total_time"] * 1000)
        total_timer_time = int(track_data["total_time"] * 1000)
        total_distance = int(track_data["total_distance"] * 100)
        total_ascent = int(track_data["total_ascent"]) if track_data["total_ascent"] else 0
        
        # Definition
        buffer.write(struct.pack("<B", 0x40 | local_msg_num))
        buffer.write(struct.pack("<BBH", 0, 0, msg_type))
        
        num_fields = 8
        if track_data["avg_heart_rate"]: num_fields += 2
        if track_data["avg_speed"]: num_fields += 2
        
        buffer.write(struct.pack("<B", num_fields))
        
        buffer.write(struct.pack("<BBB", self.FIELD_TIMESTAMP, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_START_TIME, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_TOTAL_ELAPSED_TIME, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_TOTAL_TIMER_TIME, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_TOTAL_DISTANCE, 4, 134))
        buffer.write(struct.pack("<BBB", self.FIELD_SPORT, 1, 0))
        buffer.write(struct.pack("<BBB", self.FIELD_TOTAL_ASCENT, 2, 132))
        
        if track_data["avg_heart_rate"]:
            buffer.write(struct.pack("<BBB", self.FIELD_AVG_HEART_RATE, 1, 2))
            buffer.write(struct.pack("<BBB", self.FIELD_MAX_HEART_RATE, 1, 2))
        
        if track_data["avg_speed"]:
            buffer.write(struct.pack("<BBB", self.FIELD_AVG_SPEED, 2, 132))
            buffer.write(struct.pack("<BBB", self.FIELD_MAX_SPEED, 2, 132))
        
        # Data
        buffer.write(struct.pack("<B", local_msg_num))
        buffer.write(struct.pack("<I", start_timestamp))
        buffer.write(struct.pack("<I", start_timestamp))
        buffer.write(struct.pack("<I", total_elapsed_time))
        buffer.write(struct.pack("<I", total_timer_time))
        buffer.write(struct.pack("<I", total_distance))
        buffer.write(struct.pack("<B", track_data["sport_type"]))
        buffer.write(struct.pack("<H", total_ascent))
        
        if track_data["avg_heart_rate"]:
            buffer.write(struct.pack("<B", track_data["avg_heart_rate"]))
            buffer.write(struct.pack("<B", track_data["max_heart_rate"]))
        
        if track_data["avg_speed"]:
            buffer.write(struct.pack("<H", int(track_data["avg_speed"] * 1000)))
            buffer.write(struct.pack("<H", int(track_data["max_speed"] * 1000)))
    
    def _datetime_to_fit_timestamp(self, dt: datetime) -> int:
        """
        Convert datetime to FIT timestamp.
        
        FIT uses seconds since 1989-12-31 00:00:00 UTC.
        
        Args:
            dt: Datetime to convert
            
        Returns:
            FIT timestamp (uint32)
        """
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
        
        # Ensure timezone awareness
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        delta = dt - fit_epoch
        return int(delta.total_seconds())
    
    def _calculate_crc(self, data: bytes) -> int:
        """
        Calculate CRC-16 for FIT file integrity.
        
        Args:
            data: Bytes to calculate CRC for
            
        Returns:
            CRC-16 value
        """
        crc = 0
        crc_table = [
            0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
            0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400
        ]
        
        for byte in data:
            tmp = crc_table[crc & 0xF]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ crc_table[byte & 0xF]
            
            tmp = crc_table[crc & 0xF]
            crc = (crc >> 4) & 0x0FFF
            crc = crc ^ tmp ^ crc_table[(byte >> 4) & 0xF]
        
        return crc


# Singleton instance
gpx_to_fit_converter = GPXToFITConverter()
