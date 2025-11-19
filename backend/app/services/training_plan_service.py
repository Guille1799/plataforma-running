"""
Training Plan Generator
AI-powered personalized training plan creation using Groq/Llama
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from groq import Groq

from .. import models
from ..core.config import settings


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
        context = self._build_plan_context(user, goal, recent_workouts, weeks)
        
        # Generate plan with AI
        prompt = f"""Genera un plan de entrenamiento personalizado de {weeks} semanas.

{context}

INSTRUCCIONES:
1. Crea un plan progresivo semana a semana
2. Incluye variedad: rodajes suaves, tempo, series, largo
3. Balancea volumen e intensidad
4. Incluye descansos estratégicos
5. Prepara específicamente para el objetivo

FORMATO (JSON):
{{
  "plan_name": "Nombre del plan",
  "goal_summary": "Resumen del objetivo",
  "weeks": [
    {{
      "week": 1,
      "focus": "Base aeróbica",
      "total_km": 25,
      "workouts": [
        {{
          "day": 1,
          "type": "easy_run",
          "name": "Rodaje suave",
          "distance_km": 6,
          "pace_target": "5:30-6:00 min/km",
          "notes": "Mantén conversacional"
        }},
        ...
      ]
    }},
    ...
  ],
  "nutrition_tips": ["tip1", "tip2"],
  "recovery_tips": ["tip1", "tip2"]
}}

Genera el plan completo en JSON:"""

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
            
            import json
            plan_text = completion.choices[0].message.content
            
            # Extract JSON (might be wrapped in markdown)
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON, with fallback
            try:
                plan_data = json.loads(plan_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to fix common issues
                # Remove trailing commas
                plan_text = plan_text.replace(',]', ']').replace(',}', '}')
                try:
                    plan_data = json.loads(plan_text)
                except json.JSONDecodeError:
                    # Final fallback: create a basic plan structure
                    plan_data = self._create_fallback_plan(goal, weeks)
            
            # Add metadata
            plan_data['created_at'] = datetime.utcnow().isoformat()
            plan_data['user_id'] = user.id
            plan_data['goal'] = goal
            plan_data['tokens_used'] = completion.usage.total_tokens
            
            return plan_data
            
        except Exception as e:
            raise Exception(f"Error generating plan: {str(e)}")
    
    def _build_plan_context(
        self,
        user: models.User,
        goal: Dict[str, Any],
        recent_workouts: List[models.Workout],
        weeks: int
    ) -> str:
        """Build context string for AI prompt."""
        context = f"""PERFIL DEL ATLETA:
- Nivel: {user.running_level or 'intermedio'}
- FC máxima: {user.max_heart_rate or 'No disponible'} bpm
- Entrenamientos recientes: {len(recent_workouts)} en últimas 4 semanas
"""

        if recent_workouts:
            total_km = sum(w.distance_meters for w in recent_workouts) / 1000
            avg_paces = [w.avg_pace for w in recent_workouts if w.avg_pace]
            avg_pace = sum(avg_paces) / len(avg_paces) if avg_paces else None
            
            context += f"""- Volumen semanal promedio: {total_km / 4:.1f} km
- Pace promedio: {avg_pace:.2f} min/km
- Workout más largo: {max(w.distance_meters for w in recent_workouts) / 1000:.1f} km
"""

        context += f"""
OBJETIVO:
- Tipo: {goal.get('type', 'distancia')}
- Meta: {goal.get('target', 'mejorar rendimiento')}
- Fecha objetivo: {goal.get('date', 'flexible')}
- Duración del plan: {weeks} semanas

PREFERENCIAS:
- Días disponibles: {goal.get('days_per_week', '4-5')} por semana
- Estilo de coaching: {user.coaching_style or 'balanceado'}
"""

        return context
    
    def adapt_plan(
        self,
        db: Session,
        user: models.User,
        plan_data: Dict[str, Any],
        actual_workouts: List[models.Workout]
    ) -> Dict[str, Any]:
        """
        Adapt training plan based on actual performance.
        
        Args:
            db: Database session
            user: User model
            plan_data: Current plan
            actual_workouts: Recent completed workouts
            
        Returns:
            Adapted plan for upcoming weeks
        """
        # Calculate adherence
        planned_workouts = []
        for week in plan_data.get('weeks', []):
            planned_workouts.extend(week.get('workouts', []))
        
        adherence = len(actual_workouts) / len(planned_workouts) if planned_workouts else 0
        
        # Analyze performance vs plan
        performance_context = f"""ADHERENCIA AL PLAN:
- Entrenamientos completados: {len(actual_workouts)} de {len(planned_workouts)} ({adherence*100:.0f}%)

AJUSTES NECESARIOS:
"""
        
        if adherence < 0.7:
            performance_context += "- Reducir volumen (baja adherencia)\n"
        elif adherence > 0.95:
            performance_context += "- Puede aumentar intensidad (excelente adherencia)\n"
        
        # Build adaptation prompt
        prompt = f"""{performance_context}

PLAN ACTUAL:
{json.dumps(plan_data, indent=2)}

Adapta las próximas 4 semanas del plan basándote en el progreso real.
Mantén el objetivo pero ajusta volumen e intensidad según adherencia y rendimiento.

Responde en JSON con las semanas actualizadas."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un entrenador que adapta planes según progreso real."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            import json
            adapted_text = completion.choices[0].message.content
            
            if "```json" in adapted_text:
                adapted_text = adapted_text.split("```json")[1].split("```")[0].strip()
            
            adapted_data = json.loads(adapted_text)
            adapted_data['adapted_at'] = datetime.utcnow().isoformat()
            adapted_data['tokens_used'] = completion.usage.total_tokens
            
            return adapted_data
            
        except Exception as e:
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

