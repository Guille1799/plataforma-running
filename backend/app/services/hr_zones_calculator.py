"""
Heart Rate Zones Calculator

Calculates personalized HR zones based on:
1. Observed max HR from workout history
2. Age-based formula (220 - age)
3. Manual user input

Zones (5-zone model):
- Zone 1: 50-60% (Recovery/Warm-up)
- Zone 2: 60-70% (Endurance Base)
- Zone 3: 70-80% (Tempo)
- Zone 4: 80-90% (Threshold)
- Zone 5: 90-100% (VO2 Max)
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta

def calculate_max_hr_from_workouts(db: Session, user_id: int, days: int = 90) -> Optional[int]:
    """
    Calculate max HR from recent workout history.
    
    Takes the highest observed HR from last N days.
    """
    from app import crud
    
    # Get recent workouts with HR data
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    workouts = crud.get_user_workouts(db, user_id)
    
    max_hr_observed = None
    for workout in workouts:
        if workout.start_time < cutoff_date:
            continue
        if workout.max_heart_rate and (max_hr_observed is None or workout.max_heart_rate > max_hr_observed):
            max_hr_observed = workout.max_heart_rate
    
    return max_hr_observed


def calculate_max_hr_from_age(age: int) -> int:
    """
    Calculate max HR using age-based formula.
    
    Uses traditional 220-age formula.
    For more accuracy, could use: 208 - (0.7 * age)
    """
    return 220 - age


def generate_hr_zones(max_hr: int) -> List[Dict]:
    """
    Generate 5-zone HR training zones.
    
    Args:
        max_hr: Maximum heart rate
        
    Returns:
        List of zone dictionaries with min/max values
    """
    zones = [
        {"zone": 1, "name": "Recovery", "min": int(max_hr * 0.50), "max": int(max_hr * 0.60), "description": "Warm-up and cool-down"},
        {"zone": 2, "name": "Endurance", "min": int(max_hr * 0.60), "max": int(max_hr * 0.70), "description": "Base building, long runs"},
        {"zone": 3, "name": "Tempo", "min": int(max_hr * 0.70), "max": int(max_hr * 0.80), "description": "Aerobic capacity"},
        {"zone": 4, "name": "Threshold", "min": int(max_hr * 0.80), "max": int(max_hr * 0.90), "description": "Lactate threshold"},
        {"zone": 5, "name": "VO2 Max", "min": int(max_hr * 0.90), "max": max_hr, "description": "Maximum effort"}
    ]
    return zones


def auto_calculate_and_save_zones(db: Session, user_id: int, user_age: Optional[int] = None) -> List[Dict]:
    """
    Automatically calculate and save HR zones for user.
    
    Priority:
    1. Observed max HR from workouts
    2. Age-based formula
    3. Default 180 bpm
    
    Args:
        db: Database session
        user_id: User ID
        user_age: User's age (optional)
        
    Returns:
        List of HR zones
    """
    from app import crud
    
    # Try to get max HR from workouts
    max_hr = calculate_max_hr_from_workouts(db, user_id, days=90)
    source = "observed"
    
    # Fallback to age-based
    if max_hr is None and user_age:
        max_hr = calculate_max_hr_from_age(user_age)
        source = "age_formula"
    
    # Final fallback
    if max_hr is None:
        max_hr = 180  # Conservative default
        source = "default"
    
    # Generate zones
    zones = generate_hr_zones(max_hr)
    
    # Save to user profile
    user = crud.get_user_by_id(db, user_id)
    user.max_heart_rate = max_hr
    user.hr_zones = zones
    db.commit()
    
    print(f"[HR ZONES] Generated for user {user_id}: Max HR {max_hr} ({source})")
    return zones


def get_zone_for_hr(hr: int, zones: List[Dict]) -> Optional[int]:
    """
    Determine which zone a given HR falls into.
    
    Args:
        hr: Heart rate value
        zones: List of HR zones
        
    Returns:
        Zone number (1-5) or None
    """
    for zone in zones:
        if zone['min'] <= hr <= zone['max']:
            return zone['zone']
    return None


def calculate_time_in_zones(workout_records: List[Dict], zones: List[Dict]) -> Dict[int, int]:
    """
    Calculate time spent in each HR zone during workout.
    
    Args:
        workout_records: List of HR samples with timestamps
        zones: HR zones definition
        
    Returns:
        Dict mapping zone number to seconds spent
    """
    time_in_zones = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for i in range(1, len(workout_records)):
        prev = workout_records[i-1]
        curr = workout_records[i]
        
        if 'heart_rate' not in curr or not curr['heart_rate']:
            continue
        
        # Calculate time delta
        time_delta = (curr['timestamp'] - prev['timestamp']).total_seconds()
        
        # Determine zone
        zone = get_zone_for_hr(curr['heart_rate'], zones)
        if zone:
            time_in_zones[zone] += time_delta
    
    return time_in_zones
