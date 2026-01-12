#!/usr/bin/env python
"""
Script to verify that Garmin synchronization was successful.

This script checks:
1. Number of workouts in database for the user
2. That last_garmin_sync timestamp was updated
3. That workouts have complete data (distance, time, pace, cadence, etc.)
4. Statistics about the sync

Usage:
    python backend/scripts/verify_garmin_sync.py <user_id>

Example:
    python backend/scripts/verify_garmin_sync.py 6
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
script_dir = Path(__file__).parent.resolve()
backend_dir_abs = script_dir.parent.resolve()
sys.path.insert(0, str(backend_dir_abs))

def verify_garmin_sync(user_id: int):
    """Verify that Garmin sync was successful."""
    print(f"\n{'='*70}")
    print(f"Garmin Sync Verification for User {user_id}")
    print(f"{'='*70}\n")
    
    # Change to backend directory so SQLite paths work correctly
    # Save original directory
    original_dir = os.getcwd()
    try:
        os.chdir(backend_dir_abs)
        
        from app.database import SessionLocal
        from app import models, crud
        
        db = SessionLocal()
        
        try:
            # Get user
            user = crud.get_user_by_id(db, user_id)
            if not user:
                print(f"[ERROR] User {user_id} not found!")
                return False
            
            print(f"User: {user.email}")
            print(f"Garmin Connected: {user.garmin_token is not None}")
            print(f"Garmin Email: {user.garmin_email or 'N/A'}")
            print()
            
            # Check last_garmin_sync
            print("=" * 70)
            print("1. Last Sync Timestamp")
            print("=" * 70)
            if user.last_garmin_sync:
                sync_time = user.last_garmin_sync
                time_ago = datetime.utcnow() - sync_time.replace(tzinfo=None) if sync_time.tzinfo else datetime.utcnow() - sync_time
                minutes_ago = time_ago.total_seconds() / 60
                
                print(f"  Last sync: {sync_time}")
                print(f"  Time ago: {minutes_ago:.1f} minutes")
                
                if minutes_ago < 60:
                    print(f"  [OK] Sync timestamp is recent (< 1 hour)")
                else:
                    print(f"  [WARNING] Sync timestamp is old (> 1 hour)")
            else:
                print(f"  [WARNING] last_garmin_sync is None - sync may not have completed")
            
            print()
            
            # Get workouts
            print("=" * 70)
            print("2. Workouts in Database")
            print("=" * 70)
            workouts = crud.get_user_workouts(db, user_id, limit=1000)
            total_workouts = len(workouts)
            
            print(f"  Total workouts: {total_workouts}")
            
            if total_workouts == 0:
                print(f"  [WARNING] No workouts found in database!")
                return False
            
            # Filter by source_type
            garmin_workouts = [w for w in workouts if w.source_type and ("garmin" in w.source_type.lower())]
            print(f"  Garmin workouts: {len(garmin_workouts)}")
            
            # Get recent workouts (last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_workouts = [w for w in workouts if w.start_time and w.start_time.replace(tzinfo=None) >= recent_cutoff]
            print(f"  Workouts in last 24h: {len(recent_workouts)}")
            
            # Get workouts created today (likely from sync)
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_workouts = [w for w in workouts if w.created_at and w.created_at.replace(tzinfo=None) >= today_start]
            print(f"  Workouts created today: {len(today_workouts)}")
            
            print()
            
            # Check workout data completeness
            print("=" * 70)
            print("3. Workout Data Completeness")
            print("=" * 70)
            
            if len(garmin_workouts) > 0:
                # Sample recent workouts
                sample_size = min(10, len(garmin_workouts))
                sample_workouts = garmin_workouts[:sample_size]
                
                print(f"  Analyzing {sample_size} recent Garmin workouts...")
                print()
                
                complete_count = 0
                missing_data = {
                    "distance": 0,
                    "duration": 0,
                    "pace": 0,
                    "heart_rate": 0,
                    "cadence": 0,
                    "vertical_oscillation": 0,
                    "stance_time": 0,
                }
                
                for workout in sample_workouts:
                    is_complete = True
                    
                    if not workout.distance_meters or workout.distance_meters == 0:
                        missing_data["distance"] += 1
                        is_complete = False
                    
                    if not workout.duration_seconds or workout.duration_seconds == 0:
                        missing_data["duration"] += 1
                        is_complete = False
                    
                    if not workout.avg_pace:
                        missing_data["pace"] += 1
                        is_complete = False
                    
                    if not workout.avg_heart_rate:
                        missing_data["heart_rate"] += 1
                        # Not critical, but good to have
                    
                    if not workout.avg_cadence:
                        missing_data["cadence"] += 1
                        # Not critical, but good to have
                    
                    if not workout.avg_vertical_oscillation:
                        missing_data["vertical_oscillation"] += 1
                        # Not critical
                    
                    if not workout.avg_stance_time:
                        missing_data["stance_time"] += 1
                        # Not critical
                    
                    if is_complete:
                        complete_count += 1
                
                print(f"  Complete workouts (distance + duration + pace): {complete_count}/{sample_size}")
                print()
                print(f"  Missing data breakdown:")
                for field, count in missing_data.items():
                    if count > 0:
                        print(f"    - {field}: {count}/{sample_size} workouts missing")
                
                if complete_count == sample_size:
                    print(f"  [OK] All sampled workouts have complete basic data")
                elif complete_count >= sample_size * 0.8:
                    print(f"  [OK] Most workouts ({complete_count}/{sample_size}) have complete data")
                else:
                    print(f"  [WARNING] Many workouts missing basic data ({complete_count}/{sample_size} complete)")
            else:
                print(f"  [WARNING] No Garmin workouts found to analyze")
            
            print()
            
            # Show sample workout
            print("=" * 70)
            print("4. Sample Workout Data")
            print("=" * 70)
            
            if len(garmin_workouts) > 0:
                sample = garmin_workouts[0]
                print(f"  Workout ID: {sample.id}")
                print(f"  Start time: {sample.start_time}")
                print(f"  Distance: {sample.distance_meters}m ({sample.distance_meters/1000:.2f}km)" if sample.distance_meters else "  Distance: N/A")
                print(f"  Duration: {sample.duration_seconds}s ({sample.duration_seconds/60:.1f}min)" if sample.duration_seconds else "  Duration: N/A")
                print(f"  Avg pace: {sample.avg_pace:.2f} min/km" if sample.avg_pace else "  Avg pace: N/A")
                print(f"  Avg HR: {sample.avg_heart_rate} bpm" if sample.avg_heart_rate else "  Avg HR: N/A")
                print(f"  Avg cadence: {sample.avg_cadence} spm" if sample.avg_cadence else "  Avg cadence: N/A")
                print(f"  Vertical oscillation: {sample.avg_vertical_oscillation} cm" if sample.avg_vertical_oscillation else "  Vertical oscillation: N/A")
                print(f"  Stance time: {sample.avg_stance_time} ms" if sample.avg_stance_time else "  Stance time: N/A")
                print(f"  Source type: {sample.source_type}")
            else:
                print(f"  [WARNING] No workouts to show")
            
            print()
            
            # Summary
            print("=" * 70)
            print("VERIFICATION SUMMARY")
            print("=" * 70)
            
            checks_passed = 0
            total_checks = 4
            
            # Check 1: last_garmin_sync updated
            if user.last_garmin_sync:
                time_ago = (datetime.utcnow() - user.last_garmin_sync.replace(tzinfo=None) if user.last_garmin_sync.tzinfo else datetime.utcnow() - user.last_garmin_sync).total_seconds() / 60
                if time_ago < 60:
                    print(f"[OK] last_garmin_sync updated recently")
                    checks_passed += 1
                else:
                    print(f"[ERROR] last_garmin_sync is old")
            else:
                print(f"[ERROR] last_garmin_sync is None")
            
            # Check 2: Workouts exist
            if total_workouts > 0:
                print(f"[OK] Workouts found in database ({total_workouts} total)")
                checks_passed += 1
            else:
                print(f"[ERROR] No workouts in database")
            
            # Check 3: Garmin workouts exist
            if len(garmin_workouts) > 0:
                print(f"[OK] Garmin workouts found ({len(garmin_workouts)})")
                checks_passed += 1
            else:
                print(f"[ERROR] No Garmin workouts found")
            
            # Check 4: Data completeness
            if len(garmin_workouts) > 0 and complete_count >= sample_size * 0.8:
                print(f"[OK] Workouts have complete data ({complete_count}/{sample_size} complete)")
                checks_passed += 1
            elif len(garmin_workouts) > 0:
                print(f"[WARNING] Workouts missing some data ({complete_count}/{sample_size} complete)")
                checks_passed += 0.5
            else:
                print(f"[ERROR] Cannot verify data completeness (no workouts)")
            
            print()
            print(f"Checks passed: {checks_passed}/{total_checks}")
            
            if checks_passed >= total_checks - 0.5:
                print(f"\n[OK] Sync verification PASSED!")
                return True
            elif checks_passed >= total_checks * 0.5:
                print(f"\n[WARNING] Sync verification PARTIAL - some issues detected")
                return False
            else:
                print(f"\n[ERROR] Sync verification FAILED!")
                return False
                
        finally:
            db.close()
            # Restore original directory
            os.chdir(original_dir)
            
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        # Restore original directory even on error
        try:
            os.chdir(original_dir)
        except:
            pass
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_garmin_sync.py <user_id>")
        print("Example: python verify_garmin_sync.py 6")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: user_id must be an integer")
        sys.exit(1)
    
    success = verify_garmin_sync(user_id)
    sys.exit(0 if success else 1)
