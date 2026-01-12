"""
Training Plan Generator
AI-powered personalized training plan creation using Groq/Llama
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from groq import Groq
import json
import logging
import re

from .. import models
from ..core.config import settings

logger = logging.getLogger(__name__)


class TrainingPlanService:
    """Service for AI-generated training plans."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_plan(
        self,
        db: Session,
        user: models.User,
        goal: Dict[str, Any],
        weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Generate personalized training plan based on user goals and history.
        
        Args:
            db: Database session
            user: User model
            goal: Goal dict with type, target, date
            weeks: Number of weeks for the plan
            
        Returns:
            Dict with complete training plan
        """
        # Analyze recent workouts
        recent_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user.id
        ).order_by(models.Workout.start_time.desc()).limit(20).all()
        
        # Calculate current fitness level
        if recent_workouts:
            total_distance = sum(w.distance_meters for w in recent_workouts) / 1000
            avg_pace = sum(w.avg_pace for w in recent_workouts if w.avg_pace) / len([w for w in recent_workouts if w.avg_pace])
            workouts_per_week = len(recent_workouts) / 4  # Last 4 weeks
        else:
            total_distance = 0
            avg_pace = 6.0  # default
            workouts_per_week = 0
        
        # Build context for AI
        context = self._build_plan_context(db, user, goal, recent_workouts, weeks)
        
        # Generate plan with AI - Improved prompt with better structure
        prompt = f"""Genera un plan de entrenamiento personalizado de {weeks} semanas.

{context}

INSTRUCCIONES DETALLADAS:
1. Crea un plan progresivo semana a semana con periodización adecuada
2. Incluye variedad: rodajes suaves (easy_run), tempo (tempo_run), intervalos (interval_run), largos (long_run), recuperación (recovery), cross-training
3. Balancea volumen e intensidad - aumenta gradualmente
4. Incluye descansos estratégicos (al menos 1-2 días de recuperación por semana)
5. Prepara específicamente para el objetivo establecido
6. Ajusta el volumen inicial basándote en el volumen semanal actual del atleta
7. Para cada workout, proporciona detalles completos: distancia, ritmo objetivo, zonas HR si aplica, duración estimada, notas

ESTRUCTURA JSON REQUERIDA:
{{
  "plan_name": "Nombre descriptivo del plan",
  "goal_summary": "Resumen del objetivo en 1-2 oraciones",
  "weeks": [
    {{
      "week": 1,
      "focus": "Descripción del enfoque de la semana",
      "total_km": 25.0,
      "intensity_score": 45.0,
      "workouts": [
        {{
          "day": 1,
          "type": "easy_run",
          "name": "Rodaje suave",
          "distance_km": 6.0,
          "duration_minutes": 35,
          "pace_target_min_per_km": 5.45,
          "pace_range": {{"min": 5.30, "max": 6.00}},
          "heart_rate_zones": [2],
          "heart_rate_percentage": {{"min": 65, "max": 75}},
          "rpe_target": 4,
          "intervals": null,
          "notes": "Mantén ritmo conversacional. Zona 2."
        }},
        {{
          "day": 3,
          "type": "tempo_run",
          "name": "Tempo 5K",
          "distance_km": 8.0,
          "duration_minutes": 35,
          "pace_target_min_per_km": 4.30,
          "pace_range": {{"min": 4.15, "max": 4.45}},
          "heart_rate_zones": [3, 4],
          "heart_rate_percentage": {{"min": 85, "max": 92}},
          "rpe_target": 7,
          "intervals": null,
          "notes": "Ritmo sostenido pero controlado"
        }}
      ]
    }}
  ],
  "metrics": {{
    "total_km": 300.0,
    "total_workouts": 42,
    "longest_run_km": 32.0,
    "peak_week_km": 65.0
  }},
  "nutrition_tips": [
    "Hidrátate bien antes y después de entrenamientos largos",
    "Come carbohidratos 2-3 horas antes de entrenamientos intensos"
  ],
  "recovery_tips": [
    "Prioriza el sueño - objetivo 7-9 horas",
    "Estira después de cada entrenamiento",
    "Toma días de recuperación activa si tienes molestias"
  ]
}}

IMPORTANTE:
- Genera SOLO JSON válido sin texto adicional
- El campo "day" debe ser un número de 1-7 (Lunes=1, Domingo=7)
- Todos los valores numéricos deben ser números (no strings)
- Incluye TODAS las {weeks} semanas completas
- Cada semana debe tener entre 4-6 workouts (incluyendo descansos)
- Calcula métricas totales del plan"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un entrenador profesional experto en crear planes de entrenamiento personalizados. Generas solo JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            plan_text = completion.choices[0].message.content
            
            # Extract JSON with robust parsing (multiple attempts)
            plan_data = self._parse_ai_response(plan_text, goal, weeks)
            
            # Add metadata with unique plan_id using microseconds
            from datetime import datetime as dt
            now = dt.utcnow()
            timestamp = now.strftime('%Y%m%d_%H%M%S')
            microseconds = now.microsecond // 1000  # Convert to milliseconds for shorter ID
            plan_data['plan_id'] = f"plan_{timestamp}_{microseconds}"
            plan_data['created_at'] = datetime.utcnow().isoformat()
            plan_data['user_id'] = user.id
            plan_data['goal'] = goal
            plan_data['tokens_used'] = completion.usage.total_tokens
            
            return plan_data
            
        except Exception as e:
            raise Exception(f"Error generating plan: {str(e)}")
    
    def _build_plan_context(
        self,
        db: Session,
        user: models.User,
        goal: Dict[str, Any],
        recent_workouts: List[models.Workout],
        weeks: int
    ) -> str:
        """Build comprehensive context string for AI prompt including health metrics."""
        context = f"""PERFIL DEL ATLETA:
- Nivel: {user.running_level or 'intermedio'}
- FC máxima: {user.max_heart_rate or 'No disponible'} bpm
- FC en reposo: {user.resting_heart_rate or 'No disponible'} bpm
- VO2 Max: {user.vo2_max or 'No disponible'}
- Altura: {user.height_cm or 'No disponible'} cm
- Peso: {user.weight_kg or 'No disponible'} kg
- Entrenamientos recientes: {len(recent_workouts)} en últimas 4 semanas
"""

        # Workout analysis
        if recent_workouts:
            total_km = sum(w.distance_meters for w in recent_workouts) / 1000
            avg_paces = [w.avg_pace for w in recent_workouts if w.avg_pace]
            avg_pace = sum(avg_paces) / len(avg_paces) if avg_paces else None
            workouts_per_week = len(recent_workouts) / 4 if len(recent_workouts) >= 4 else len(recent_workouts)
            
            context += f"""- Volumen semanal promedio: {total_km / max(4, len(recent_workouts) / workouts_per_week) if workouts_per_week > 0 else total_km:.1f} km
- Pace promedio: {avg_pace:.2f} min/km
- Workout más largo: {max(w.distance_meters for w in recent_workouts) / 1000:.1f} km
- Distancia total últimos 30 días: {total_km:.1f} km
"""

        # Health metrics context
        try:
            recent_health = db.query(models.HealthMetric).filter(
                models.HealthMetric.user_id == user.id,
                models.HealthMetric.date >= date.today() - timedelta(days=14)
            ).order_by(models.HealthMetric.date.desc()).limit(7).all()
            
            if recent_health:
                health_metrics_text = "\nMÉTRICAS DE SALUD (últimas 2 semanas):\n"
                
                hrv_values = [h.hrv_ms for h in recent_health if h.hrv_ms]
                if hrv_values:
                    avg_hrv = sum(hrv_values) / len(hrv_values)
                    health_metrics_text += f"- HRV promedio: {avg_hrv:.0f} ms (últimos {len(recent_health)} días)\n"
                
                readiness_values = [h.readiness_score for h in recent_health if h.readiness_score]
                if readiness_values:
                    avg_readiness = sum(readiness_values) / len(readiness_values)
                    health_metrics_text += f"- Readiness promedio: {avg_readiness:.0f}/100\n"
                
                sleep_values = [h.sleep_duration_minutes for h in recent_health if h.sleep_duration_minutes]
                if sleep_values:
                    avg_sleep = sum(sleep_values) / len(sleep_values)
                    health_metrics_text += f"- Sueño promedio: {avg_sleep/60:.1f} horas/noche\n"
                
                if health_metrics_text != "\nMÉTRICAS DE SALUD (últimas 2 semanas):\n":
                    context += health_metrics_text
        except Exception as e:
            logger.warning(f"Error fetching health metrics for context: {e}")

        # Injury considerations
        if user.injuries:
            active_injuries = [inj for inj in user.injuries if isinstance(inj, dict) and not inj.get('recovered', True)]
            if active_injuries:
                context += f"""
LESIONES ACTIVAS:
- Consideraciones: {', '.join([inj.get('type', '') + ': ' + inj.get('description', '')[:50] for inj in active_injuries[:3]])}
"""

        context += f"""
OBJETIVO:
- Tipo: {goal.get('type', 'distancia')}
- Meta: {goal.get('target', 'mejorar rendimiento')}
- Fecha objetivo: {goal.get('date', 'flexible')}
- Duración del plan: {weeks} semanas
- Volumen semanal actual: {goal.get('current_weekly_km', 0)} km/semana
- Notas: {goal.get('notes', 'Ninguna')}

PREFERENCIAS:
- Días disponibles: {goal.get('days_per_week', '4-5')} por semana
- Estilo de coaching: {user.coaching_style or 'balanceado'}
- Zonas HR: {'Configuradas' if user.hr_zones else 'No configuradas'}
"""

        return context
    
    def _parse_ai_response(
        self,
        response_text: str,
        goal: Dict[str, Any],
        weeks: int,
        max_attempts: int = 5
    ) -> Dict[str, Any]:
        """Parse AI response with multiple attempts and JSON fixing.
        
        Args:
            response_text: Raw response from AI
            goal: Goal dictionary for fallback
            weeks: Number of weeks for fallback
            max_attempts: Maximum parsing attempts
            
        Returns:
            Parsed plan data dictionary
        """
        # Extract JSON from markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Remove any leading/trailing whitespace
        response_text = response_text.strip()
        
        # Multiple parsing attempts with different fixes
        for attempt in range(max_attempts):
            try:
                plan_data = json.loads(response_text)
                # Validate basic structure
                if self._validate_plan_structure(plan_data, weeks):
                    return plan_data
                else:
                    logger.warning(f"Plan structure validation failed on attempt {attempt + 1}")
            except json.JSONDecodeError as e:
                if attempt < max_attempts - 1:
                    # Try to fix common JSON issues
                    response_text = self._fix_json_common_issues(response_text)
                    logger.debug(f"JSON parse error on attempt {attempt + 1}: {e}. Retrying with fixes...")
                else:
                    logger.error(f"Failed to parse JSON after {max_attempts} attempts: {e}")
                    logger.debug(f"Response text (first 500 chars): {response_text[:500]}")
        
        # Final fallback: create a basic plan structure
        logger.warning("Using fallback plan due to parsing failures")
        return self._create_fallback_plan(goal, weeks)
    
    def _fix_json_common_issues(self, json_text: str) -> str:
        """Fix common JSON issues in AI responses.
        
        Args:
            json_text: JSON string with potential issues
            
        Returns:
            Fixed JSON string
        """
        # Remove trailing commas before ] or }
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix single quotes to double quotes for keys only (be careful)
        # Only fix key:value pairs, not strings
        json_text = re.sub(r"'(\w+)':\s*", r'"\1": ', json_text)
        
        # Remove comments (// or /* */)
        json_text = re.sub(r'//.*?$', '', json_text, flags=re.MULTILINE)
        json_text = re.sub(r'/\*.*?\*/', '', json_text, flags=re.DOTALL)
        
        return json_text
    
    def _validate_plan_structure(self, plan_data: Dict[str, Any], expected_weeks: int) -> bool:
        """Validate that plan has correct structure.
        
        Args:
            plan_data: Parsed plan dictionary
            expected_weeks: Expected number of weeks
            
        Returns:
            True if structure is valid, False otherwise
        """
        try:
            # Check required top-level fields
            if not isinstance(plan_data, dict):
                return False
            
            if "plan_name" not in plan_data or "weeks" not in plan_data:
                return False
            
            # Check weeks structure
            weeks = plan_data.get("weeks", [])
            if not isinstance(weeks, list):
                return False
            
            # Check we have at least expected number of weeks
            if len(weeks) < expected_weeks:
                logger.warning(f"Plan has {len(weeks)} weeks but expected {expected_weeks}")
                return False
            
            # Validate first week structure as sample
            if len(weeks) > 0:
                first_week = weeks[0]
                if not isinstance(first_week, dict):
                    return False
                if "week" not in first_week or "workouts" not in first_week:
                    return False
                if not isinstance(first_week.get("workouts"), list):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating plan structure: {e}")
            return False
    
    def adapt_plan(
        self,
        db: Session,
        user: models.User,
        plan_data: Dict[str, Any],
        actual_workouts: List[models.Workout],
        health_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adapt training plan based on actual performance and health metrics.
        
        Args:
            db: Database session
            user: User model
            plan_data: Current plan
            actual_workouts: Recent completed workouts
            health_metrics: Optional health metrics (HRV, readiness, sleep, etc.)
            
        Returns:
            Adapted plan for upcoming weeks
        """
        # Get health metrics if not provided
        if health_metrics is None:
            try:
                recent_health = db.query(models.HealthMetric).filter(
                    models.HealthMetric.user_id == user.id,
                    models.HealthMetric.date >= date.today() - timedelta(days=7)
                ).order_by(models.HealthMetric.date.desc()).limit(7).all()
                
                if recent_health:
                    health_metrics = {
                        'avg_hrv': sum(h.hrv_ms for h in recent_health if h.hrv_ms) / len([h for h in recent_health if h.hrv_ms]) if any(h.hrv_ms for h in recent_health) else None,
                        'avg_readiness': sum(h.readiness_score for h in recent_health if h.readiness_score) / len([h for h in recent_health if h.readiness_score]) if any(h.readiness_score for h in recent_health) else None,
                        'avg_sleep': sum(h.sleep_duration_minutes for h in recent_health if h.sleep_duration_minutes) / len([h for h in recent_health if h.sleep_duration_minutes]) if any(h.sleep_duration_minutes for h in recent_health) else None,
                        'avg_stress': sum(h.stress_level for h in recent_health if h.stress_level) / len([h for h in recent_health if h.stress_level]) if any(h.stress_level for h in recent_health) else None,
                    }
            except Exception as e:
                logger.warning(f"Error fetching health metrics for adaptation: {e}")
                health_metrics = {}
        
        # Calculate adherence and performance metrics
        planned_workouts = []
        for week in plan_data.get('weeks', []):
            planned_workouts.extend(week.get('workouts', []))
        
        adherence = len(actual_workouts) / len(planned_workouts) if planned_workouts else 0
        
        # Analyze actual performance
        if actual_workouts:
            actual_avg_pace = sum(w.avg_pace for w in actual_workouts if w.avg_pace) / len([w for w in actual_workouts if w.avg_pace]) if any(w.avg_pace for w in actual_workouts) else None
            actual_total_km = sum(w.distance_meters for w in actual_workouts) / 1000
            planned_total_km = sum(w.get('distance_km', 0) for w in planned_workouts[:len(actual_workouts)])
            volume_deviation = ((actual_total_km - planned_total_km) / planned_total_km * 100) if planned_total_km > 0 else 0
        else:
            actual_avg_pace = None
            volume_deviation = 0
        
        # Build comprehensive context
        performance_context = f"""ADHERENCIA AL PLAN:
- Entrenamientos completados: {len(actual_workouts)} de {len(planned_workouts)} ({adherence*100:.0f}%)
- Volumen realizado vs planificado: {volume_deviation:+.1f}%
"""
        
        if actual_avg_pace:
            performance_context += f"- Ritmo promedio real: {actual_avg_pace/60:.2f} min/km\n"
        
        # Health metrics context
        if health_metrics:
            health_context = "\nMÉTRICAS DE SALUD (última semana):\n"
            if health_metrics.get('avg_hrv'):
                hrv = health_metrics['avg_hrv']
                health_context += f"- HRV promedio: {hrv:.0f} ms "
                if hrv < 30:
                    health_context += "(⚠️ Bajo - considerar recuperación)\n"
                elif hrv > 50:
                    health_context += "(✓ Bueno)\n"
                else:
                    health_context += "(Moderado)\n"
            
            if health_metrics.get('avg_readiness'):
                readiness = health_metrics['avg_readiness']
                health_context += f"- Readiness promedio: {readiness:.0f}/100 "
                if readiness < 50:
                    health_context += "(⚠️ Bajo - reducir carga)\n"
                elif readiness > 75:
                    health_context += "(✓ Excelente - puede aumentar)\n"
                else:
                    health_context += "(Moderado)\n"
            
            if health_metrics.get('avg_sleep'):
                sleep = health_metrics['avg_sleep'] / 60
                health_context += f"- Sueño promedio: {sleep:.1f} horas/noche "
                if sleep < 6:
                    health_context += "(⚠️ Insuficiente)\n"
                elif sleep >= 7:
                    health_context += "(✓ Adecuado)\n"
                else:
                    health_context += "(Moderado)\n"
            
            performance_context += health_context
        
        # Adaptation recommendations
        recommendations = []
        if adherence < 0.7:
            recommendations.append("- Reducir volumen semanal (baja adherencia)")
        elif adherence > 0.95:
            recommendations.append("- Puede aumentar intensidad ligeramente (excelente adherencia)")
        
        if volume_deviation < -20:
            recommendations.append("- Volumen muy por debajo - reducir objetivos")
        elif volume_deviation > 30:
            recommendations.append("- Volumen muy por encima - riesgo de sobreentrenamiento")
        
        if health_metrics:
            if health_metrics.get('avg_readiness') and health_metrics['avg_readiness'] < 50:
                recommendations.append("- Readiness bajo - aumentar recuperación, reducir intensidad")
            if health_metrics.get('avg_hrv') and health_metrics['avg_hrv'] < 30:
                recommendations.append("- HRV bajo - priorizar descanso")
        
        performance_context += "\nRECOMENDACIONES DE AJUSTE:\n"
        for rec in recommendations:
            performance_context += f"{rec}\n"
        
        # Build adaptation prompt
        prompt = f"""{performance_context}

PLAN ACTUAL (últimas semanas completadas):
{json.dumps({k: v for k, v in plan_data.items() if k != 'weeks'}, indent=2)}

Semanas del plan actual (para referencia):
{json.dumps(plan_data.get('weeks', [])[-4:], indent=2)}

OBJETIVO: Adapta las próximas 4 semanas del plan basándote en:
1. Progreso real (adherencia, volumen realizado)
2. Métricas de salud (HRV, readiness, sueño)
3. Rendimiento actual vs objetivos

INSTRUCCIONES:
- Mantén el objetivo general del plan
- Ajusta volumen e intensidad según el análisis
- Incrementa progresión si el rendimiento es mejor de lo esperado
- Reduce carga si hay signos de fatiga o baja adherencia
- Incluye semanas de recuperación si es necesario

Responde SOLO con JSON válido conteniendo las semanas adaptadas (misma estructura que el plan actual)."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un entrenador experto que adapta planes de entrenamiento basándote en datos reales de rendimiento y salud. Generas solo JSON válido con semanas adaptadas."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            adapted_text = completion.choices[0].message.content
            
            # Parse with robust parsing
            adapted_weeks = self._parse_ai_response(
                adapted_text,
                {'type': 'adaptation'},
                4,  # 4 weeks
                max_attempts=3
            )
            
            # Ensure we have weeks structure
            if 'weeks' not in adapted_weeks:
                # If AI returned just weeks array, wrap it
                if isinstance(adapted_weeks, list):
                    adapted_weeks = {'weeks': adapted_weeks}
            
            adapted_weeks['adapted_at'] = datetime.utcnow().isoformat()
            adapted_weeks['tokens_used'] = completion.usage.total_tokens
            adapted_weeks['adaptation_reason'] = '; '.join(recommendations) if recommendations else 'Ajuste basado en progreso'
            
            return adapted_weeks
            
        except Exception as e:
            logger.error(f"Error adapting plan: {e}", exc_info=True)
            raise Exception(f"Error adapting plan: {str(e)}")
    
    def _create_fallback_plan(self, goal: Dict[str, Any], weeks: int) -> Dict[str, Any]:
        """Create a basic fallback training plan when AI generation fails."""
        goal_type = goal.get('type', 'general')
        
        # Build basic weekly structure
        weeks_data = []
        for week_num in range(1, weeks + 1):
            week_focus = {
                1: "Aerobic Base",
                2: "Building Volume", 
                3: "Speed Work",
                4: "Recovery Week"
            }.get(week_num % 4 or 4, "Progressive Training")
            
            weeks_data.append({
                "week": week_num,
                "focus": week_focus,
                "total_km": 30 + (week_num * 2) if week_num % 4 != 0 else 25,
                "workouts": [
                    {
                        "day": 1,
                        "type": "easy_run",
                        "name": "Easy Run",
                        "distance_km": 6,
                        "pace_target": "5:30-6:00 min/km",
                        "notes": "Keep conversation pace"
                    },
                    {
                        "day": 3,
                        "type": "tempo_run",
                        "name": "Tempo Run",
                        "distance_km": 8,
                        "pace_target": "4:30-5:00 min/km",
                        "notes": "Sustained effort"
                    },
                    {
                        "day": 5,
                        "type": "interval_run",
                        "name": "Interval Training",
                        "distance_km": 10,
                        "pace_target": "4:00-4:30 min/km",
                        "notes": "Include warm-up and cool-down"
                    },
                    {
                        "day": 7,
                        "type": "long_run",
                        "name": "Long Run",
                        "distance_km": 12 + (week_num * 0.5),
                        "pace_target": "5:45-6:15 min/km",
                        "notes": "Build endurance"
                    }
                ]
            })
        
        return {
            "plan_name": f"{goal_type.title()} Training Plan - {weeks} Weeks",
            "goal_summary": f"Personalized {weeks}-week plan for {goal_type} training",
            "weeks": weeks_data,
            "nutrition_tips": [
                "Carb-load before long runs",
                "Hydrate consistently during training",
                "Protein recovery post-workout"
            ],
            "recovery_tips": [
                "Take easy days seriously",
                "Prioritize sleep",
                "Use foam rolling for recovery"
            ]
        }
    
    def calculate_plan_duration_with_target_race(
        self,
        target_race_date: datetime,
        goal_type: str,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate plan duration automatically based on target race date.
        
        Uses periodization science to determine optimal preparation time:
        - 5K: 8-12 weeks (recommend 10)
        - 10K: 10-14 weeks (recommend 12)
        - Half Marathon: 12-16 weeks (recommend 14)
        - Marathon: 16-20 weeks (recommend 18)
        
        Args:
            target_race_date: Target race/event date
            goal_type: Type of goal (5k, 10k, half_marathon, marathon)
            start_date: Plan start date (default: today)
            
        Returns:
            Dict with calculated weeks, race date, plan start date
        """
        if not start_date:
            start_date = datetime.utcnow()
        
        # Validate race is in future
        if target_race_date <= start_date:
            raise ValueError("Target race date must be in the future")
        
        # Calculate days available
        days_available = (target_race_date - start_date).days
        weeks_available = days_available / 7
        
        # Recommended durations per goal type
        recommendations = {
            "5k": {
                "min_weeks": 8,
                "max_weeks": 12,
                "recommended_weeks": 10,
                "min_days_before_race": 3,
                "name": "5K Sprint"
            },
            "10k": {
                "min_weeks": 10,
                "max_weeks": 14,
                "recommended_weeks": 12,
                "min_days_before_race": 4,
                "name": "10K"
            },
            "half_marathon": {
                "min_weeks": 12,
                "max_weeks": 16,
                "recommended_weeks": 14,
                "min_days_before_race": 5,
                "name": "Half Marathon"
            },
            "marathon": {
                "min_weeks": 16,
                "max_weeks": 20,
                "recommended_weeks": 18,
                "min_days_before_race": 7,
                "name": "Marathon"
            },
            "improve_fitness": {
                "min_weeks": 8,
                "max_weeks": 16,
                "recommended_weeks": 12,
                "min_days_before_race": 2,
                "name": "General Fitness"
            },
            "build_endurance": {
                "min_weeks": 12,
                "max_weeks": 16,
                "recommended_weeks": 14,
                "min_days_before_race": 3,
                "name": "Build Endurance"
            }
        }
        
        goal_recommendation = recommendations.get(goal_type, recommendations["improve_fitness"])
        min_days_for_taper = goal_recommendation["min_days_before_race"]
        
        # Calculate optimal weeks
        optimal_weeks = goal_recommendation["recommended_weeks"]
        max_possible_weeks = weeks_available - (min_days_for_taper / 7)
        
        if max_possible_weeks < goal_recommendation["min_weeks"]:
            # Not enough time for optimal plan
            return {
                "feasible": False,
                "error": f"Insufficient time for {goal_type}. Need at least {goal_recommendation['min_weeks']} weeks + {min_days_for_taper} days taper. You have {weeks_available:.1f} weeks.",
                "weeks_available": weeks_available,
                "weeks_needed": goal_recommendation["min_weeks"],
                "taper_days": min_days_for_taper,
                "goal_type": goal_type,
                "target_race_date": target_race_date.isoformat()
            }
        
        # Calculate actual duration
        actual_weeks = min(optimal_weeks, int(max_possible_weeks))
        plan_end_date = start_date + timedelta(weeks=actual_weeks)
        taper_start_date = target_race_date - timedelta(days=min_days_for_taper)
        
        return {
            "feasible": True,
            "goal_type": goal_type,
            "goal_name": goal_recommendation["name"],
            "plan_weeks": actual_weeks,
            "plan_start_date": start_date.isoformat(),
            "plan_end_date": plan_end_date.isoformat(),
            "target_race_date": target_race_date.isoformat(),
            "taper_start_date": taper_start_date.isoformat(),
            "taper_weeks": (min_days_for_taper / 7),
            "training_weeks": actual_weeks - (min_days_for_taper / 7),
            "weeks_available": weeks_available,
            "recommendation": f"Optimal plan de {actual_weeks} semanas: {actual_weeks - int(min_days_for_taper / 7)} semanas de entrenamiento + {int(min_days_for_taper / 7)} semana(s) de descarga"
        }
    
    def get_plan_duration_options(
        self,
        goal_type: str
    ) -> Dict[str, Any]:
        """Get recommended plan duration options when no target race is specified.
        
        Returns multiple duration options with recommendations.
        
        Args:
            goal_type: Type of goal (5k, 10k, half_marathon, marathon, improve_fitness, etc)
            
        Returns:
            Dict with multiple duration options and recommendations
        """
        options = {
            "5k": {
                "name": "5K Sprint",
                "options": [
                    {
                        "weeks": 8,
                        "label": "Quick Preparation",
                        "description": "Mínimo recomendado si ya tienes base aeróbica",
                        "focus": "Velocidad y eficiencia",
                        "recommended": False
                    },
                    {
                        "weeks": 10,
                        "label": "Optimal Preparation",
                        "description": "Equilibrio perfecto entre construcción de fitness y ajuste específico",
                        "focus": "Speed work + tempo runs",
                        "recommended": True
                    },
                    {
                        "weeks": 12,
                        "label": "Extended Preparation",
                        "description": "Si tienes poco volumen de entrenamiento actual",
                        "focus": "Construcción gradual + velocidad",
                        "recommended": False
                    }
                ]
            },
            "10k": {
                "name": "10K",
                "options": [
                    {
                        "weeks": 10,
                        "label": "Quick Preparation",
                        "description": "Para corredores con buena base",
                        "focus": "Velocidad y resistencia",
                        "recommended": False
                    },
                    {
                        "weeks": 12,
                        "label": "Optimal Preparation",
                        "description": "Plan equilibrado recomendado para la mayoría",
                        "focus": "Tempo + intervalos + rodaje largo",
                        "recommended": True
                    },
                    {
                        "weeks": 14,
                        "label": "Extended Preparation",
                        "description": "Para construir base sólida antes de intensidad",
                        "focus": "Periodización completa",
                        "recommended": False
                    }
                ]
            },
            "half_marathon": {
                "name": "Half Marathon",
                "options": [
                    {
                        "weeks": 12,
                        "label": "Accelerated Program",
                        "description": "Solo si ya tienes volumen de 35+ km/semana",
                        "focus": "Velocidad e intensidad",
                        "recommended": False
                    },
                    {
                        "weeks": 14,
                        "label": "Optimal Preparation",
                        "description": "Plan científico con periodización completa",
                        "focus": "Construcción progresiva con picos",
                        "recommended": True
                    },
                    {
                        "weeks": 16,
                        "label": "Extended Program",
                        "description": "Para máxima preparación y solidificación",
                        "focus": "Base sólida + pico óptimo",
                        "recommended": False
                    }
                ]
            },
            "marathon": {
                "name": "Marathon",
                "options": [
                    {
                        "weeks": 16,
                        "label": "Accelerated Program",
                        "description": "Solo para corredores experimentados con 50+ km/semana",
                        "focus": "Máxima intensidad y resistencia",
                        "recommended": False
                    },
                    {
                        "weeks": 18,
                        "label": "Optimal Preparation",
                        "description": "Plan recomendado con periodización científica",
                        "focus": "Construcción sólida de aeróbica + pico de largo",
                        "recommended": True
                    },
                    {
                        "weeks": 20,
                        "label": "Full Training Cycle",
                        "description": "Máxima preparación y confianza",
                        "focus": "Tiempo para desarrollo completo",
                        "recommended": False
                    }
                ]
            },
            "improve_fitness": {
                "name": "Mejorar Fitness",
                "options": [
                    {
                        "weeks": 8,
                        "label": "Quick Start",
                        "description": "Primera toma de contacto con plan estructurado",
                        "focus": "Construir hábito y base",
                        "recommended": False
                    },
                    {
                        "weeks": 12,
                        "label": "Optimal Program",
                        "description": "Mejora significativa de fitness cardiovascular",
                        "focus": "Aeróbica + resistencia",
                        "recommended": True
                    },
                    {
                        "weeks": 16,
                        "label": "Long Term Development",
                        "description": "Transformación completa del fitness",
                        "focus": "Mejora gradual y sostenible",
                        "recommended": False
                    }
                ]
            },
            "build_endurance": {
                "name": "Construir Resistencia",
                "options": [
                    {
                        "weeks": 10,
                        "label": "Quick Foundation",
                        "description": "Construcción rápida de resistencia",
                        "focus": "Rodajes largos y aeróbica",
                        "recommended": False
                    },
                    {
                        "weeks": 14,
                        "label": "Optimal Program",
                        "description": "Plan completo para resistencia sólida",
                        "focus": "Periodización con énfasis en volumen",
                        "recommended": True
                    },
                    {
                        "weeks": 16,
                        "label": "Extended Development",
                        "description": "Máxima construcción de resistencia base",
                        "focus": "Aeróbica de larga duración",
                        "recommended": False
                    }
                ]
            }
        }
        
        goal_options = options.get(goal_type, options["improve_fitness"])
        
        return {
            "goal_type": goal_type,
            "goal_name": goal_options["name"],
            "duration_options": goal_options["options"],
            "message": f"Elige la duración de tu plan de {goal_options['name']}. La opción recomendada está marcada."
        }


# Lazy loading singleton
_training_plan_service_instance = None

def get_training_plan_service() -> "TrainingPlanService":
    """Get or create the training plan service singleton."""
    global _training_plan_service_instance
    if _training_plan_service_instance is None:
        _training_plan_service_instance = TrainingPlanService()
    return _training_plan_service_instance

