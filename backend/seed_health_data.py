"""
Seed health metrics with sample data for testing
Creates 30 days of realistic health data
"""
import sys
from datetime import date, timedelta
from random import randint, uniform, choice
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import User, HealthMetric, Base

def seed_health_metrics(user_id: int, days: int = 30):
    """Generate sample health metrics for testing."""
    db = SessionLocal()
    
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ User with id {user_id} not found")
            return
        
        print(f"🌱 Seeding {days} days of health metrics for user {user.email}...")
        
        # Base values (simulate a reasonably fit runner)
        base_hrv = 65  # ms
        base_resting_hr = 52  # bpm
        base_sleep = 450  # minutes (7.5 hours)
        base_body_battery = 75
        base_stress = 30
        
        metrics_created = 0
        
        for day_offset in range(days):
            metric_date = date.today() - timedelta(days=days - day_offset - 1)
            
            # Check if metric already exists for this date
            existing = db.query(HealthMetric).filter(
                HealthMetric.user_id == user_id,
                HealthMetric.date == metric_date
            ).first()
            
            if existing:
                print(f"  ⏭️  Skipping {metric_date} (already exists)")
                continue
            
            # Add some variability and trends
            # Simulate recovery cycles (good days after hard workouts)
            recovery_factor = 1.0 if day_offset % 7 < 5 else 0.85  # Harder on weekends
            
            # Calculate metrics with realistic variation
            hrv_variation = uniform(-10, 15) * recovery_factor
            hrv = max(40, min(90, base_hrv + hrv_variation))
            
            resting_hr_variation = uniform(-3, 5) * (2 - recovery_factor)
            resting_hr = int(max(45, min(65, base_resting_hr + resting_hr_variation)))
            
            sleep_variation = uniform(-60, 60)
            sleep_minutes = int(max(300, min(600, base_sleep + sleep_variation)))
            sleep_score = int(min(100, max(40, (sleep_minutes / 480) * 100 + uniform(-10, 10))))
            
            # Calculate sleep stages (rough approximation)
            deep_sleep = int(sleep_minutes * uniform(0.15, 0.25))
            rem_sleep = int(sleep_minutes * uniform(0.20, 0.30))
            light_sleep = sleep_minutes - deep_sleep - rem_sleep - int(sleep_minutes * 0.05)
            awake_minutes = int(sleep_minutes * 0.05)
            
            body_battery_variation = uniform(-15, 15) * recovery_factor
            body_battery = int(max(20, min(100, base_body_battery + body_battery_variation)))
            
            stress_variation = uniform(-10, 15) * (2 - recovery_factor)
            stress = int(max(10, min(80, base_stress + stress_variation)))
            
            # Steps and activity (more on training days)
            is_training_day = day_offset % 7 < 5
            steps = randint(8000, 15000) if is_training_day else randint(4000, 8000)
            calories = int(steps * 0.04 + randint(1800, 2200))
            active_calories = int(steps * 0.03 + randint(300, 600) if is_training_day else randint(150, 300))
            intensity_minutes = randint(30, 90) if is_training_day else randint(0, 30)
            
            # Subjective metrics (1-5 scale)
            energy_level = int(min(5, max(1, 3 + (body_battery - 75) / 20)))
            soreness_level = int(min(5, max(1, 3 - (recovery_factor - 0.9) * 10)))
            mood = int(min(5, max(1, 3 + uniform(-1, 1))))
            motivation = int(min(5, max(1, 3 + (energy_level - 3) * 0.5)))
            
            # Calculate baselines (7-day rolling average)
            baseline_start = metric_date - timedelta(days=7)
            recent_metrics = db.query(HealthMetric).filter(
                HealthMetric.user_id == user_id,
                HealthMetric.date >= baseline_start,
                HealthMetric.date < metric_date
            ).all()
            
            if recent_metrics:
                hrv_baseline = sum(m.hrv_ms for m in recent_metrics if m.hrv_ms) / len(recent_metrics)
                resting_hr_baseline = sum(m.resting_hr_bpm for m in recent_metrics if m.resting_hr_bpm) / len(recent_metrics)
            else:
                hrv_baseline = base_hrv
                resting_hr_baseline = base_resting_hr
            
            # Calculate readiness score
            readiness_factors = []
            if body_battery:
                readiness_factors.append(body_battery * 0.4)
            if sleep_score:
                readiness_factors.append(sleep_score * 0.3)
            if hrv and hrv_baseline:
                hrv_ratio = hrv / hrv_baseline
                readiness_factors.append(min(100, hrv_ratio * 100) * 0.2)
            if resting_hr and resting_hr_baseline:
                rhr_ratio = resting_hr_baseline / resting_hr
                readiness_factors.append(min(100, rhr_ratio * 100) * 0.1)
            
            readiness_score = int(sum(readiness_factors)) if readiness_factors else None
            
            # Data quality
            metric_count = sum([
                1 if hrv else 0,
                1 if resting_hr else 0,
                1 if body_battery else 0,
                1 if sleep_minutes else 0,
                1 if stress else 0,
            ])
            data_quality = 'high' if metric_count >= 4 else 'medium' if metric_count >= 2 else 'basic'
            
            # Create metric
            metric = HealthMetric(
                user_id=user_id,
                date=metric_date,
                hrv_ms=round(hrv, 1),
                resting_hr_bpm=resting_hr,
                hrv_baseline_ms=round(hrv_baseline, 1),
                resting_hr_baseline_bpm=int(resting_hr_baseline),
                sleep_duration_minutes=sleep_minutes,
                sleep_score=sleep_score,
                deep_sleep_minutes=deep_sleep,
                rem_sleep_minutes=rem_sleep,
                light_sleep_minutes=light_sleep,
                awake_minutes=awake_minutes,
                body_battery=body_battery,
                readiness_score=readiness_score,
                stress_level=stress,
                recovery_score=body_battery,  # Use body battery as recovery proxy
                steps=steps,
                calories_burned=calories,
                active_calories=active_calories,
                intensity_minutes=intensity_minutes,
                respiration_rate=randint(12, 18),
                spo2_percentage=uniform(95.0, 99.0),
                energy_level=energy_level,
                soreness_level=soreness_level,
                mood=mood,
                motivation=motivation,
                notes=None if uniform(0, 1) > 0.3 else choice([
                    "Sentí buena energía hoy",
                    "Piernas un poco cansadas",
                    "Excelente recuperación",
                    "Día de descanso necesario",
                    "Listo para entrenar duro"
                ]),
                source='garmin',
                data_quality=data_quality
            )
            
            db.add(metric)
            metrics_created += 1
            
            if day_offset % 5 == 0:
                db.commit()  # Commit every 5 days
                print(f"  ✓ Created metrics up to {metric_date}")
        
        db.commit()
        print(f"\n✅ Successfully seeded {metrics_created} health metrics")
        print(f"📊 Date range: {date.today() - timedelta(days=days)} to {date.today() - timedelta(days=1)}")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Health Metrics Seeder")
    print("=" * 50)
    
    # Get user_id from command line or use default
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    seed_health_metrics(user_id, days)
    
    print("\n💡 Now you can:")
    print("  1. Visit http://localhost:3000/health to see your readiness score")
    print("  2. Visit http://localhost:3000/health/history to see trends")
    print("  3. Complete daily check-in to add more data")
