"""
coach_service.py - AI Coach service using Groq API

Provides personalized coaching based on:
- Workout analysis
- Athlete profile and goals
- Training history
- HR zones and performance metrics
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from groq import Groq
import os
import logging

from app import models
from app.core.config import settings

logger = logging.getLogger(__name__)


class CoachService:
    """AI Coach service for personalized training feedback."""
    
    def __init__(self):
        """Initialize Groq client."""
        api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    # ========================================================================
    # HR ZONES CALCULATION (Scientific Karvonen Formula + Power Zones)
    # ========================================================================
    
    def calculate_hr_zones(
        self, 
        max_hr: int,
        resting_hr: int = 60,
        ftp_watts: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate 7-zone heart rate training zones using Karvonen formula.
        
        Uses the Karvonen formula: (Max HR - Resting HR) * percentage + Resting HR
        This is more accurate than simple max HR percentages.
        
        Also calculates power zones (watts) if FTP is provided.
        
        Args:
            max_hr: Maximum heart rate in bpm
            resting_hr: Resting heart rate (default: 60 bpm)
            ftp_watts: Functional Threshold Power (optional, for power zones)
            
        Returns:
            Dict with zones and their characteristics including power zones
        """
        logger.info(f"📊 Calculating HR zones: max_hr={max_hr}, resting_hr={resting_hr}, ftp_watts={ftp_watts}")
        
        # Karvonen formula: HRR = Max HR - Resting HR
        hrr = max_hr - resting_hr
        
        # Calculate power zones if FTP is provided
        power_zones = {}
        if ftp_watts:
            power_zones = self._calculate_power_zones(ftp_watts)
        
        return {
            "zone_1": {
                "name": "Recovery (Z1)",
                "hr": {
                    "min_bpm": int(hrr * 0.50 + resting_hr),
                    "max_bpm": int(hrr * 0.60 + resting_hr),
                    "percentage": "50-60% HRR",
                },
                "power": power_zones.get("z1") if power_zones else None,
                "description": "Recuperación activa - conversación normal",
                "duration": "45-120 min",
                "intensity": "muy baja",
                "purpose": "Recuperación, adaptación fisiológica"
            },
            "zone_2": {
                "name": "Aerobic Base (Z2)",
                "hr": {
                    "min_bpm": int(hrr * 0.60 + resting_hr),
                    "max_bpm": int(hrr * 0.70 + resting_hr),
                    "percentage": "60-70% HRR",
                },
                "power": power_zones.get("z2") if power_zones else None,
                "description": "Base aeróbica - ritmo cómodo y sostenible",
                "duration": "90-180 min",
                "intensity": "baja",
                "purpose": "Construir aerobic base, aumentar resistencia"
            },
            "zone_3": {
                "name": "Sweet Spot (Z3)",
                "hr": {
                    "min_bpm": int(hrr * 0.70 + resting_hr),
                    "max_bpm": int(hrr * 0.80 + resting_hr),
                    "percentage": "70-80% HRR",
                },
                "power": power_zones.get("z3") if power_zones else None,
                "description": "Sweet spot - esfuerzo moderado, conversación difícil",
                "duration": "20-90 min",
                "intensity": "moderada",
                "purpose": "Mejorar umbral aeróbico, resistencia"
            },
            "zone_4": {
                "name": "Threshold (Z4)",
                "hr": {
                    "min_bpm": int(hrr * 0.80 + resting_hr),
                    "max_bpm": int(hrr * 0.90 + resting_hr),
                    "percentage": "80-90% HRR",
                },
                "power": power_zones.get("z4") if power_zones else None,
                "description": "Umbral anaeróbico - esfuerzo alto, sin conversación",
                "duration": "10-40 min",
                "intensity": "alta",
                "purpose": "Mejorar ritmo de carrera, umbral de lactato"
            },
            "zone_5": {
                "name": "VO2 Max (Z5)",
                "hr": {
                    "min_bpm": int(hrr * 0.90 + resting_hr),
                    "max_bpm": max_hr,
                    "percentage": "90-100% HRR",
                },
                "power": power_zones.get("z5") if power_zones else None,
                "description": "Máxima intensidad - esfuerzo máximo (anaeróbico)",
                "duration": "3-8 min",
                "intensity": "muy alta",
                "purpose": "Mejorar VO2 Max, capacidad anaeróbica"
            }
        }
        
        logger.info(f"✅ HR zones calculated successfully - 5 zones with Karvonen formula")
    
    def _calculate_power_zones(self, ftp_watts: int) -> Dict[str, Dict[str, Any]]:
        """Calculate power zones based on FTP (Functional Threshold Power).
        
        Uses standard cycling power zone distribution:
        Z1: < 55% FTP
        Z2: 55-75% FTP
        Z3: 75-90% FTP
        Z4: 90-105% FTP
        Z5: 105-120% FTP
        Z6: 120-150% FTP
        Z7: > 150% FTP
        
        Args:
            ftp_watts: Functional Threshold Power in watts
            
        Returns:
            Dict with power zone ranges
        """
        return {
            "z1": {
                "name": "Active Recovery",
                "min_watts": 0,
                "max_watts": int(ftp_watts * 0.55),
                "percentage": "<55%"
            },
            "z2": {
                "name": "Endurance",
                "min_watts": int(ftp_watts * 0.55),
                "max_watts": int(ftp_watts * 0.75),
                "percentage": "55-75%"
            },
            "z3": {
                "name": "Tempo",
                "min_watts": int(ftp_watts * 0.75),
                "max_watts": int(ftp_watts * 0.90),
                "percentage": "75-90%"
            },
            "z4": {
                "name": "Threshold",
                "min_watts": int(ftp_watts * 0.90),
                "max_watts": int(ftp_watts * 1.05),
                "percentage": "90-105%"
            },
            "z5": {
                "name": "VO2 Max",
                "min_watts": int(ftp_watts * 1.05),
                "max_watts": int(ftp_watts * 1.20),
                "percentage": "105-120%"
            },
            "z6": {
                "name": "Anaerobic Capacity",
                "min_watts": int(ftp_watts * 1.20),
                "max_watts": int(ftp_watts * 1.50),
                "percentage": "120-150%"
            },
            "z7": {
                "name": "Neuromuscular Power",
                "min_watts": int(ftp_watts * 1.50),
                "max_watts": int(ftp_watts * 2.0),
                "percentage": ">150%"
            }
        }
    
    def identify_workout_zone(
        self, 
        avg_hr: int, 
        max_hr: int,
        resting_hr: int = 60
    ) -> str:
        """Identify which HR zone a workout was performed in using Karvonen formula.
        
        Args:
            avg_hr: Average heart rate during workout
            max_hr: User's maximum heart rate
            resting_hr: User's resting heart rate (default: 60)
            
        Returns:
            Zone name (zone_1, zone_2, etc.)
        """
        zones = self.calculate_hr_zones(max_hr, resting_hr)
        
        for zone_key, zone_info in zones.items():
            if zone_info["hr"]["min_bpm"] <= avg_hr <= zone_info["hr"]["max_bpm"]:
                return zone_key
        
        # Default to zone_2 if not found
        return "zone_2"
    
    # ========================================================================
    # ATHLETE CONTEXT BUILDER
    # ========================================================================
    
    def build_athlete_context(
        self, 
        user: models.User,
        recent_workouts: List[models.Workout],
        goals: Optional[List[Dict]] = None
    ) -> str:
        """Build comprehensive athlete context for AI prompts.
        
        Args:
            user: User model with profile data
            recent_workouts: List of recent workouts
            goals: Optional list of training goals
            
        Returns:
            Formatted context string for AI
        """
        context_parts = []
        
        # Basic profile
        context_parts.append(f"PERFIL DEL ATLETA:")
        context_parts.append(f"- Nombre: {user.name}")
        context_parts.append(f"- Nivel: {user.running_level or 'intermediate'}")
        
        if user.max_heart_rate:
            context_parts.append(f"- FCM: {user.max_heart_rate} bpm")
            zones = self.calculate_hr_zones(user.max_heart_rate)
            context_parts.append(f"- Zonas cardíacas:")
            for zone_key, zone_info in zones.items():
                context_parts.append(f"  {zone_info['name']}: {zone_info['min_bpm']}-{zone_info['max_bpm']} bpm")
        
        # Goals
        if goals and len(goals) > 0:
            context_parts.append(f"\nOBJETIVOS:")
            for goal in goals:
                if not goal.get("completed"):
                    target = goal.get("target_value", "N/A")
                    deadline = goal.get("deadline", "Sin fecha límite")
                    context_parts.append(f"- {goal['name']} (Objetivo: {target}, Fecha: {deadline})")
        
        # Recent training history
        if recent_workouts:
            context_parts.append(f"\nHISTORIAL RECIENTE ({len(recent_workouts)} entrenamientos):")
            
            total_distance = sum(w.distance_meters / 1000 for w in recent_workouts)
            total_time = sum(w.duration_seconds / 3600 for w in recent_workouts)
            avg_pace = sum(w.avg_pace for w in recent_workouts if w.avg_pace) / len([w for w in recent_workouts if w.avg_pace]) if any(w.avg_pace for w in recent_workouts) else 0
            
            context_parts.append(f"- Distancia total: {total_distance:.1f} km")
            context_parts.append(f"- Tiempo total: {total_time:.1f} horas")
            if avg_pace > 0:
                context_parts.append(f"- Pace promedio: {self._format_pace(avg_pace)}")
            
            # Last 3 workouts summary
            context_parts.append(f"\nÚltimos 3 entrenamientos:")
            for i, workout in enumerate(recent_workouts[:3], 1):
                date_str = workout.start_time.strftime("%d/%m/%Y")
                distance = workout.distance_meters / 1000
                pace_str = self._format_pace(workout.avg_pace) if workout.avg_pace else "N/A"
                hr_str = f"{workout.avg_heart_rate} bpm" if workout.avg_heart_rate else "N/A"
                context_parts.append(f"  {i}. {date_str}: {distance:.1f}km, pace {pace_str}, FC {hr_str}")
        
        # Injuries
        if user.injuries and len(user.injuries) > 0:
            active_injuries = [inj for inj in user.injuries if not inj.get("recovered")]
            if active_injuries:
                context_parts.append(f"\nLESIONES ACTIVAS:")
                for injury in active_injuries:
                    context_parts.append(f"- {injury.get('injury_type')}: {injury.get('description', 'N/A')}")
        
        # Preferences
        if user.preferences:
            context_parts.append(f"\nPREFERENCIAS:")
            if user.preferences.get("time_of_day"):
                context_parts.append(f"- Horario preferido: {user.preferences['time_of_day']}")
            if user.preferences.get("terrain_preference"):
                context_parts.append(f"- Terreno preferido: {user.preferences['terrain_preference']}")
        
        return "\n".join(context_parts)
    
    # ========================================================================
    # COACHING STYLE PROMPTS
    # ========================================================================
    
    def get_coaching_style_prompt(self, style: str, custom_prompt: Optional[str] = None) -> str:
        """Get system prompt based on coaching style.
        
        Args:
            style: Coaching style (motivator/technical/balanced/custom)
            custom_prompt: Custom prompt if style is 'custom'
            
        Returns:
            System prompt for AI
        """
        if style == "custom" and custom_prompt:
            return custom_prompt
        
        style_prompts = {
            "motivator": """Eres un coach de running energético y motivador. Tu estilo es:
- Positivo y entusiasta
- Enfocado en celebrar logros
- Usa emojis y lenguaje animado
- Das ánimos incluso en entrenamientos difíciles
- Destacas el progreso y la mejora continua
- Usas metáforas inspiradoras""",
            
            "technical": """Eres un coach de running analítico y técnico. Tu estilo es:
- Basado en datos y métricas
- Enfocado en eficiencia y técnica
- Explicaciones detalladas de fisiología
- Recomendaciones específicas con números
- Referencias a zonas cardíacas, pace, cadencia
- Científico pero accesible""",
            
            "balanced": """Eres un coach de running profesional y equilibrado. Tu estilo es:
- Mix de motivación y técnica
- Reconoces logros pero también señalas áreas de mejora
- Usas datos pero sin abrumar
- Consejos prácticos y accionables
- Tono amigable y profesional
- Adaptas tu enfoque según el contexto"""
        }
        
        return style_prompts.get(style, style_prompts["balanced"])
    
    # ========================================================================
    # POST-WORKOUT ANALYSIS
    # ========================================================================
    
    def analyze_workout(
        self,
        workout: models.Workout,
        user: models.User,
        recent_workouts: List[models.Workout],
        db: Session
    ) -> Dict[str, Any]:
        """Analyze workout and provide AI coaching feedback.
        
        Args:
            workout: Workout to analyze
            user: User who performed the workout
            recent_workouts: Recent workout history
            db: Database session
            
        Returns:
            Dict with analysis, recommendations, and metrics
        """
        # Build context
        goals = user.goals if user.goals else []
        athlete_context = self.build_athlete_context(user, recent_workouts, goals)
        
        # Prepare workout details
        workout_details = self._format_workout_details(workout, user)
        
        # Get coaching style
        coaching_style = user.coaching_style or "balanced"
        custom_prompt = user.preferences.get("custom_prompt") if user.preferences else None
        system_prompt = self.get_coaching_style_prompt(coaching_style, custom_prompt)
        
        # Build AI prompt
        user_prompt = f"""Analiza este entrenamiento de running y proporciona feedback personalizado.

{athlete_context}

ENTRENAMIENTO A ANALIZAR:
{workout_details}

Proporciona:
1. **Resumen del esfuerzo** (1-2 líneas): Evalúa la calidad del entrenamiento
2. **Análisis técnico** (2-3 puntos clave): Pace, FC, zonas cardíacas
3. **Recomendación para próximo entrenamiento** (específica y accionable)
4. **Emoji de reacción** al final

Sé conciso pero útil. Máximo 200 palabras."""
        
        # Call Groq API
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_feedback = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            return {
                "workout_id": workout.id,
                "analysis": ai_feedback,
                "tokens_used": tokens_used,
                "coaching_style": coaching_style,
                "workout_summary": {
                    "distance_km": round(workout.distance_meters / 1000, 2),
                    "duration_min": round(workout.duration_seconds / 60, 1),
                    "avg_pace": self._format_pace(workout.avg_pace) if workout.avg_pace else None,
                    "avg_hr": workout.avg_heart_rate,
                    "zone": self.identify_workout_zone(workout.avg_heart_rate, user.max_heart_rate) if workout.avg_heart_rate and user.max_heart_rate else None
                }
            }
            
        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _format_workout_details(self, workout: models.Workout, user: models.User) -> str:
        """Format workout details for AI prompt."""
        details = []
        
        details.append(f"Fecha: {workout.start_time.strftime('%d/%m/%Y %H:%M')}")
        details.append(f"Distancia: {workout.distance_meters / 1000:.2f} km")
        details.append(f"Duración: {workout.duration_seconds // 60} min {workout.duration_seconds % 60} seg")
        
        if workout.avg_pace:
            details.append(f"Pace promedio: {self._format_pace(workout.avg_pace)}")
        
        if workout.avg_heart_rate:
            details.append(f"FC promedio: {workout.avg_heart_rate} bpm")
            if workout.max_heart_rate:
                details.append(f"FC máxima: {workout.max_heart_rate} bpm")
            
            if user.max_heart_rate:
                zone = self.identify_workout_zone(workout.avg_heart_rate, user.max_heart_rate)
                zones = self.calculate_hr_zones(user.max_heart_rate)
                zone_info = zones.get(zone)
                if zone_info:
                    details.append(f"Zona cardíaca: {zone_info['name']} ({zone_info['percentage']})")
        
        if workout.elevation_gain:
            details.append(f"Desnivel positivo: {workout.elevation_gain:.0f} m")
        
        if workout.calories:
            details.append(f"Calorías: {workout.calories:.0f} kcal")
        
        return "\n".join([f"- {d}" for d in details])
    
    def _format_pace(self, pace_seconds_per_km: float) -> str:
        """Format pace from seconds per km to min:sec/km."""
        if not pace_seconds_per_km or pace_seconds_per_km <= 0:
            return "N/A"
        
        minutes = int(pace_seconds_per_km // 60)
        seconds = int(pace_seconds_per_km % 60)
        return f"{minutes}:{seconds:02d}/km"
    
    # ========================================================================
    # WEEKLY TRAINING PLAN GENERATION
    # ========================================================================
    
    def generate_weekly_plan(
        self,
        user: models.User,
        recent_workouts: List[models.Workout],
        start_date: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Generate personalized weekly training plan.
        
        Args:
            user: User for whom to generate plan
            recent_workouts: Recent workout history
            start_date: Start date for plan (default: next Monday)
            db: Database session
            
        Returns:
            Dict with weekly plan and recommendations
        """
        # Determine start date (next Monday if not specified)
        if not start_date:
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            start_date = today + timedelta(days=days_until_monday)
        
        # Build context
        goals = user.goals if user.goals else []
        athlete_context = self.build_athlete_context(user, recent_workouts, goals)
        
        # Get coaching style
        coaching_style = user.coaching_style or "balanced"
        custom_prompt = user.preferences.get("custom_prompt") if user.preferences else None
        system_prompt = self.get_coaching_style_prompt(coaching_style, custom_prompt)
        
        # Calculate weekly volume from recent workouts
        if recent_workouts:
            recent_distances = [w.distance_meters / 1000 for w in recent_workouts[:4]]
            avg_weekly_volume = sum(recent_distances)
        else:
            avg_weekly_volume = 20  # Default 20km/week
        
        # Build prompt for weekly plan
        user_prompt = f"""Genera un plan de entrenamiento semanal personalizado de running.

{athlete_context}

VOLUMEN ACTUAL: {avg_weekly_volume:.1f} km/semana

INSTRUCCIONES:
1. Crea un plan de 7 días (de {start_date.strftime('%d/%m')} a {(start_date + timedelta(days=6)).strftime('%d/%m')})
2. Incluye 3-4 días de running y 3-4 días de descanso/recuperación activa
3. Varía las intensidades: base aeróbica, tempo, intervalos
4. Incluye distancias específicas y ritmos objetivo
5. Considera los objetivos del atleta
6. Progresión gradual (no aumentar más de 10% semanal)

FORMATO:
Para cada día indica:
- Día (Lunes, Martes, etc)
- Tipo de entrenamiento
- Distancia/duración
- Ritmo/zona cardíaca objetivo
- Objetivo del entrenamiento

Máximo 300 palabras."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            plan_text = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            return {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": (start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                "plan": plan_text,
                "weekly_volume_km": avg_weekly_volume,
                "tokens_used": tokens_used,
                "coaching_style": coaching_style,
                "goals": [g for g in goals if not g.get("completed")]
            }
            
        except Exception as e:
            raise Exception(f"Error generating weekly plan: {str(e)}")
    
    # ========================================================================
    # FORM & TECHNIQUE ANALYSIS
    # ========================================================================
    
    def analyze_running_form(
        self,
        workout: models.Workout,
        user: models.User
    ) -> Dict[str, Any]:
        """Analyze running form from workout metrics.
        
        Analyzes cadence, vertical oscillation, ground contact time, etc.
        
        Args:
            workout: Workout to analyze
            user: User who performed workout
            
        Returns:
            Dict with form analysis and recommendations
        """
        form_metrics = {}
        issues = []
        recommendations = []
        
        # Note: These metrics would come from FIT file parsing
        # For now we'll use what we have and suggest what to look for
        
        # Pace analysis
        if workout.avg_pace:
            form_metrics["pace"] = self._format_pace(workout.avg_pace)
            
            # Check for pace consistency
            if workout.max_speed and workout.distance_meters > 0:
                avg_speed = (workout.distance_meters / 1000) / (workout.duration_seconds / 3600)
                speed_variance = abs(workout.max_speed - avg_speed) / avg_speed
                
                if speed_variance > 0.3:
                    issues.append("Gran variación en velocidad durante el entrenamiento")
                    recommendations.append("Trabaja en mantener un ritmo más constante, especialmente en entrenamientos de base")
        
        # Heart rate analysis
        if workout.avg_heart_rate and workout.max_heart_rate:
            hr_variance = workout.max_heart_rate - workout.avg_heart_rate
            form_metrics["hr_avg"] = workout.avg_heart_rate
            form_metrics["hr_max"] = workout.max_heart_rate
            form_metrics["hr_variance"] = hr_variance
            
            if hr_variance > 30:
                issues.append("Alta variabilidad de frecuencia cardíaca")
                recommendations.append("Considera hacer warm-up más largo y mantener ritmo más controlado")
        
        # Elevation analysis
        if workout.elevation_gain and workout.distance_meters:
            elevation_per_km = workout.elevation_gain / (workout.distance_meters / 1000)
            form_metrics["elevation_per_km"] = round(elevation_per_km, 1)
            
            if elevation_per_km > 50:
                recommendations.append("Terreno con mucho desnivel: enfócate en pasos cortos y mantén cadencia alta en subidas")
        
        # Duration vs distance efficiency
        if workout.duration_seconds and workout.distance_meters:
            pace_seconds = workout.duration_seconds / (workout.distance_meters / 1000)
            form_metrics["efficiency"] = "good" if pace_seconds < 360 else "moderate" if pace_seconds < 420 else "low"
        
        # Build form analysis with AI
        form_summary = self._generate_form_analysis_ai(form_metrics, issues, recommendations, user)
        
        return {
            "workout_id": workout.id,
            "form_metrics": form_metrics,
            "issues_detected": issues,
            "recommendations": recommendations,
            "ai_analysis": form_summary,
            "note": "Para análisis más detallado, asegúrate de que tu Garmin registre: cadencia, oscilación vertical, tiempo de contacto con el suelo"
        }
    
    def _generate_form_analysis_ai(
        self,
        metrics: Dict[str, Any],
        issues: List[str],
        recommendations: List[str],
        user: models.User
    ) -> str:
        """Generate AI-powered form analysis."""
        coaching_style = user.coaching_style or "balanced"
        system_prompt = self.get_coaching_style_prompt(coaching_style, None)
        
        user_prompt = f"""Analiza la técnica de running basándote en estas métricas:

MÉTRICAS:
{chr(10).join([f'- {k}: {v}' for k, v in metrics.items()])}

PROBLEMAS DETECTADOS:
{chr(10).join([f'- {i}' for i in issues]) if issues else '- Ninguno detectado'}

Proporciona:
1. Evaluación de la técnica (2-3 líneas)
2. Recomendaciones específicas para mejorar (2-3 puntos concretos)
3. Ejercicios o drills sugeridos

Máximo 150 palabras."""
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return completion.choices[0].message.content
        except:
            return "Análisis técnico no disponible en este momento."
    
    # ========================================================================
    # CHATBOT WITH MEMORY
    # ========================================================================
    
    def chat_with_coach(
        self,
        user: models.User,
        user_message: str,
        conversation_history: List[models.ChatMessage],
        recent_workouts: List[models.Workout],
        db: Session
    ) -> Dict[str, Any]:
        """Chat with AI coach maintaining conversation context.
        
        Args:
            user: User chatting with coach
            user_message: User's message
            conversation_history: Previous messages in conversation
            recent_workouts: Recent workout history for context
            db: Database session
            
        Returns:
            Dict with assistant response and metadata
        """
        # Build athlete context
        goals = user.goals if user.goals else []
        athlete_context = self.build_athlete_context(user, recent_workouts, goals)
        
        # Get coaching style
        coaching_style = user.coaching_style or "balanced"
        custom_prompt = user.preferences.get("custom_prompt") if user.preferences else None
        system_prompt = self.get_coaching_style_prompt(coaching_style, custom_prompt)
        
        # Enhanced system prompt with context
        enhanced_system_prompt = f"""{system_prompt}

CONTEXTO DEL ATLETA:
{athlete_context}

Eres el coach personal del usuario. Tienes acceso a todo su historial de entrenamientos, objetivos y progreso.
Responde de manera conversacional, útil y personalizada. Puedes:
- Dar consejos de entrenamiento
- Responder preguntas técnicas sobre running
- Motivar y animar
- Sugerir workouts específicos
- Analizar progreso
- Ayudar con nutrición, recuperación, etc.

Mantén respuestas concisas (máximo 200 palabras) a menos que se solicite más detalle."""
        
        # Build conversation messages for API
        messages = [{"role": "system", "content": enhanced_system_prompt}]
        
        # Add recent conversation history (last 10 messages for context)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            
            assistant_response = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            return {
                "response": assistant_response,
                "tokens_used": tokens_used,
                "coaching_style": coaching_style,
                "conversation_length": len(conversation_history) + 2  # +2 for new messages
            }
            
        except Exception as e:
            raise Exception(f"Error in chat: {str(e)}")
    
    # ========================================================================
    # DEEP WORKOUT ANALYSIS (NEW)
    # ========================================================================
    
    def analyze_workout_deep(
        self,
        db: Session,
        user: models.User,
        workout: models.Workout
    ) -> Dict[str, Any]:
        """
        Análisis profundo de entrenamiento:
        - Análisis del workout actual
        - Comparación con entrenamientos similares
        - Análisis técnico (cadencia, TCS, etc)
        - Mejoras sugeridas
        - Plan de entrenamientos personalizados
        
        Args:
            db: Database session
            user: User model
            workout: Workout to analyze
            
        Returns:
            Dict with comprehensive analysis
        """
        # Get similar workouts (same distance range ±20%)
        distance_min = workout.distance_meters * 0.8
        distance_max = workout.distance_meters * 1.2
        
        similar_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user.id,
            models.Workout.id != workout.id,
            models.Workout.sport_type == workout.sport_type,
            models.Workout.distance_meters >= distance_min,
            models.Workout.distance_meters <= distance_max
        ).order_by(models.Workout.start_time.desc()).limit(5).all()
        
        # Build context
        workout_context = self._build_workout_context(workout, user)
        
        # Build comparison context
        comparison_context = ""
        if similar_workouts:
            comparison_context = "\n\nENTRENAMIENTOS SIMILARES (para comparación):\n"
            for i, w in enumerate(similar_workouts, 1):
                comparison_context += f"{i}. {w.start_time.strftime('%Y-%m-%d')}: "
                comparison_context += f"{w.distance_meters/1000:.2f}km en {w.duration_seconds//60}min "
                comparison_context += f"(pace {w.avg_pace:.2f} min/km, "
                comparison_context += f"FC {w.avg_heart_rate or 'N/A'} bpm)\n"
        
        # Build goals context
        goals_context = ""
        if user.goals:
            goals_context = "\n\nOBJETIVOS DEL ATLETA:\n"
            for goal in user.goals[:3]:
                goals_context += f"- {goal.get('target', 'N/A')} ({goal.get('type', 'N/A')})\n"
        
        # Create comprehensive prompt
        prompt = f"""Analiza este entrenamiento de manera exhaustiva y profesional.

{workout_context}
{comparison_context}
{goals_context}

ANÁLISIS REQUERIDO:

1. **ANÁLISIS DEL ENTRENAMIENTO**
   - Evalúa la intensidad del esfuerzo (zona cardíaca, pace, duración)
   - Identifica el tipo de entrenamiento realizado (rodaje, tempo, series, etc)
   - Valora si fue apropiado para los objetivos

2. **COMPARACIÓN CON ENTRENAMIENTOS SIMILARES**
   - Compara el rendimiento con entrenamientos previos similares
   - Identifica tendencias (¿está mejorando, estancado, retrocediendo?)
   - Destaca diferencias significativas en pace, FC, o sensaciones

3. **ANÁLISIS TÉCNICO DE FORMA DE CARRERA**
   - Cadencia: evalúa si está en rango óptimo (170-180 pasos/min)
   - Tiempo de contacto (TCS): menor es mejor (<250ms ideal)
   - Oscilación vertical: menor es más eficiente (<8cm ideal)
   - Balance izq/der: detecta asimetrías significativas (>52/48 = problema)
   - Rigidez de piernas: valora economía de movimiento

4. **ÁREAS DE MEJORA**
   - Identifica 2-3 aspectos concretos a trabajar
   - Prioriza según impacto en rendimiento y objetivos
   - Sé específico y accionable

5. **PLAN DE ENTRENAMIENTOS RECOMENDADOS**
   - Sugiere 3-4 entrenamientos específicos para la próxima semana
   - Incluye: tipo, distancia/duración, intensidad (zona HR), objetivo
   - Alinea con objetivos del atleta
   - Balance entre trabajo duro y recuperación

Responde en español, de manera estructurada pero natural. Sé directo y práctico."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un entrenador profesional de running con amplia experiencia en análisis biomecánico y planificación de entrenamientos. Tu objetivo es ayudar al atleta a mejorar de manera inteligente y sostenible."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            return {
                "analysis": analysis,
                "workout_id": workout.id,
                "similar_workouts_count": len(similar_workouts),
                "tokens_used": tokens_used,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error in deep analysis: {str(e)}")
    
    def _build_workout_context(self, workout: models.Workout, user: models.User) -> str:
        """Build detailed context string for a workout."""
        context = f"""ENTRENAMIENTO A ANALIZAR:
Fecha: {workout.start_time.strftime('%Y-%m-%d %H:%M')}
Tipo: {workout.sport_type}
Distancia: {workout.distance_meters/1000:.2f} km
Duración: {workout.duration_seconds//60} min {workout.duration_seconds%60} seg
Pace promedio: {workout.avg_pace:.2f} min/km
FC promedio: {workout.avg_heart_rate or 'N/A'} bpm
FC máxima: {workout.max_heart_rate or 'N/A'} bpm"""

        # Add form metrics if available
        if workout.avg_cadence:
            context += f"\nCadencia promedio: {workout.avg_cadence:.0f} pasos/min"
        if workout.avg_stance_time:
            context += f"\nTiempo de contacto: {workout.avg_stance_time:.0f} ms"
        if workout.avg_vertical_oscillation:
            context += f"\nOscilación vertical: {workout.avg_vertical_oscillation:.1f} cm"
        if workout.left_right_balance:
            left = workout.left_right_balance
            right = 100 - left
            context += f"\nBalance izq/der: {left:.0f}% / {right:.0f}%"
        if workout.avg_leg_spring_stiffness:
            context += f"\nRigidez de piernas: {workout.avg_leg_spring_stiffness:.2f}"
        if workout.elevation_gain:
            context += f"\nDesnivel: {workout.elevation_gain:.0f} m"
        
        # Add user context
        context += f"\n\nPERFIL DEL ATLETA:"
        context += f"\nNivel: {user.running_level or 'intermedio'}"
        if user.max_heart_rate:
            context += f"\nFC máxima: {user.max_heart_rate} bpm"
        
        return context
    
    # ========================================================================
    # HEALTH METRICS & READINESS SCORE
    # ========================================================================
    
    def calculate_readiness_score(
        self,
        health_metric: Optional[models.HealthMetric],
        user: models.User
    ) -> Dict[str, Any]:
        """
        Calculate 0-100 readiness score based on health metrics.
        
        Args:
            health_metric: Today's health metrics (can be None)
            user: User model
            
        Returns:
            Dict with readiness_score, factors, and recommendation
        """
        if not health_metric:
            return {
                "readiness_score": 50,
                "confidence": "low",
                "factors": [],
                "recommendation": "No health data available. Train based on how you feel.",
                "should_train_hard": None
            }
        
        factors = []
        total_weight = 0
        weighted_sum = 0
        
        # Factor 1: Body Battery / Readiness Score (40% weight)
        if health_metric.body_battery is not None:
            score = health_metric.body_battery
            weight = 0.4
            factors.append({
                "name": "Body Battery",
                "score": score,
                "weight": weight,
                "status": "good" if score >= 70 else "moderate" if score >= 50 else "low"
            })
            weighted_sum += score * weight
            total_weight += weight
        elif health_metric.readiness_score is not None:
            score = health_metric.readiness_score
            weight = 0.4
            factors.append({
                "name": "Readiness",
                "score": score,
                "weight": weight,
                "status": "good" if score >= 70 else "moderate" if score >= 50 else "low"
            })
            weighted_sum += score * weight
            total_weight += weight
        
        # Factor 2: Sleep Quality (30% weight)
        if health_metric.sleep_score is not None:
            score = health_metric.sleep_score
            weight = 0.3
            factors.append({
                "name": "Sleep Quality",
                "score": score,
                "weight": weight,
                "status": "good" if score >= 70 else "moderate" if score >= 50 else "poor"
            })
            weighted_sum += score * weight
            total_weight += weight
        elif health_metric.sleep_duration_minutes is not None:
            # Convert sleep duration to score (7-9h = 100, < 6h = low)
            hours = health_metric.sleep_duration_minutes / 60
            if hours >= 7:
                score = min(100, 100 * (hours / 8))
            else:
                score = max(0, (hours / 7) * 100)
            weight = 0.25
            factors.append({
                "name": "Sleep Duration",
                "score": int(score),
                "weight": weight,
                "status": "good" if hours >= 7 else "moderate" if hours >= 6 else "poor"
            })
            weighted_sum += score * weight
            total_weight += weight
        
        # Factor 3: HRV vs Baseline (20% weight)
        if health_metric.hrv_ms and health_metric.hrv_baseline_ms:
            ratio = health_metric.hrv_ms / health_metric.hrv_baseline_ms
            score = min(100, ratio * 100)
            weight = 0.2
            status = "good" if ratio >= 0.95 else "moderate" if ratio >= 0.85 else "low"
            factors.append({
                "name": "HRV",
                "score": int(score),
                "weight": weight,
                "status": status,
                "detail": f"{health_metric.hrv_ms:.0f}ms (baseline: {health_metric.hrv_baseline_ms:.0f}ms)"
            })
            weighted_sum += score * weight
            total_weight += weight
        
        # Factor 4: Resting HR vs Baseline (10% weight)
        if health_metric.resting_hr_bpm and health_metric.resting_hr_baseline_bpm:
            # Lower resting HR is better, so invert the scale
            diff = health_metric.resting_hr_bpm - health_metric.resting_hr_baseline_bpm
            if diff <= 0:
                score = 100  # Lower or equal to baseline = perfect
            else:
                score = max(0, 100 - (diff * 10))  # Each bpm above baseline = -10 points
            weight = 0.1
            status = "good" if diff <= 2 else "moderate" if diff <= 5 else "elevated"
            factors.append({
                "name": "Resting HR",
                "score": int(score),
                "weight": weight,
                "status": status,
                "detail": f"{health_metric.resting_hr_bpm} bpm (baseline: {health_metric.resting_hr_baseline_bpm} bpm)"
            })
            weighted_sum += score * weight
            total_weight += weight
        
        # Factor 5: Stress Level (10% weight)
        if health_metric.stress_level is not None:
            # Invert stress (low stress = high score)
            score = 100 - health_metric.stress_level
            weight = 0.1
            factors.append({
                "name": "Stress",
                "score": score,
                "weight": weight,
                "status": "low" if health_metric.stress_level < 30 else "moderate" if health_metric.stress_level < 60 else "high"
            })
            weighted_sum += score * weight
            total_weight += weight
        
        # Factor 6: Subjective Energy (if manual entry)
        if health_metric.energy_level is not None:
            # Convert 1-5 scale to 0-100
            score = (health_metric.energy_level - 1) * 25
            weight = 0.15
            factors.append({
                "name": "Energy Level",
                "score": score,
                "weight": weight,
                "status": "high" if health_metric.energy_level >= 4 else "moderate" if health_metric.energy_level >= 3 else "low"
            })
            weighted_sum += score * weight
            total_weight += weight
        
        # Calculate final score
        if total_weight == 0:
            readiness_score = 50
            confidence = "low"
        else:
            readiness_score = int(weighted_sum / total_weight)
            confidence = "high" if total_weight >= 0.6 else "medium" if total_weight >= 0.3 else "low"
        
        # Generate recommendation
        if readiness_score >= 75:
            recommendation = "✅ Excelente estado de recuperación. Perfecto para entrenamientos intensos."
            should_train_hard = True
        elif readiness_score >= 60:
            recommendation = "⚠️ Estado moderado. Entrenamientos ligeros o moderados recomendados."
            should_train_hard = False
        else:
            recommendation = "🛑 Estado de recuperación bajo. Considera día de descanso o recuperación activa."
            should_train_hard = False
        
        return {
            "readiness_score": readiness_score,
            "confidence": confidence,
            "factors": factors,
            "recommendation": recommendation,
            "should_train_hard": should_train_hard
        }
    
    def generate_health_aware_recommendation(
        self,
        db: Session,
        user: models.User,
        health_metric: Optional[models.HealthMetric] = None
    ) -> Dict[str, Any]:
        """
        Generate workout recommendation based on health metrics.
        
        Args:
            db: Database session
            user: User model
            health_metric: Today's health metrics
            
        Returns:
            Dict with readiness, recommendation, and suggested workout
        """
        from datetime import date
        
        # Get today's health metrics if not provided
        if not health_metric:
            health_metric = db.query(models.HealthMetric).filter(
                models.HealthMetric.user_id == user.id,
                models.HealthMetric.date == date.today()
            ).first()
        
        # Calculate readiness
        readiness = self.calculate_readiness_score(health_metric, user)
        
        # Get recent workouts for context
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user.id,
            models.Workout.start_time >= week_ago
        ).order_by(models.Workout.start_time.desc()).all()
        
        # Build context for AI
        health_context = self._build_health_context(health_metric, readiness)
        athlete_context = self.build_athlete_context(user, recent_workouts, user.goals)
        
        # Generate AI recommendation
        prompt = f"""
{health_context}

{athlete_context}

Based on the athlete's current health state and training history, provide:
1. A personalized workout recommendation for today
2. Specific intensity guidance (HR zones or pace)
3. Duration and distance suggestions
4. Any precautions or modifications needed
5. Recovery advice if needed

Keep the response in Spanish, conversational, and motivating while being realistic about their current state.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.get_coaching_style_prompt(user.coaching_style or "balanced")
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            ai_recommendation = response.choices[0].message.content
            
        except Exception as e:
            print(f"[COACH] Error generating AI recommendation: {e}")
            ai_recommendation = readiness["recommendation"]
        
        return {
            "readiness": readiness,
            "ai_recommendation": ai_recommendation,
            "health_metrics": self._format_health_metrics(health_metric) if health_metric else None
        }
    
    def _build_health_context(
        self,
        health_metric: Optional[models.HealthMetric],
        readiness: Dict[str, Any]
    ) -> str:
        """Build health context string for AI prompts."""
        if not health_metric:
            return "ESTADO DE SALUD: No hay datos disponibles hoy"
        
        lines = ["ESTADO DE SALUD HOY:"]
        lines.append(f"- Readiness Score: {readiness['readiness_score']}/100 ({readiness['confidence']} confidence)")
        
        for factor in readiness["factors"]:
            detail = factor.get("detail", "")
            lines.append(f"- {factor['name']}: {factor['score']}/100 ({factor['status']}) {detail}")
        
        if health_metric.sleep_duration_minutes:
            hours = health_metric.sleep_duration_minutes / 60
            lines.append(f"- Sueño: {hours:.1f}h")
            if health_metric.deep_sleep_minutes:
                deep_hours = health_metric.deep_sleep_minutes / 60
                lines.append(f"  - Sueño profundo: {deep_hours:.1f}h")
        
        if health_metric.steps:
            lines.append(f"- Pasos: {health_metric.steps:,}")
        
        if health_metric.notes:
            lines.append(f"- Notas del atleta: {health_metric.notes}")
        
        lines.append(f"\n{readiness['recommendation']}")
        
        return "\n".join(lines)
    
    def _format_health_metrics(self, health_metric: models.HealthMetric) -> Dict[str, Any]:
        """Format health metrics for API response."""
        return {
            "date": health_metric.date.isoformat(),
            "hrv_ms": health_metric.hrv_ms,
            "resting_hr_bpm": health_metric.resting_hr_bpm,
            "sleep_duration_hours": health_metric.sleep_duration_minutes / 60 if health_metric.sleep_duration_minutes else None,
            "sleep_score": health_metric.sleep_score,
            "body_battery": health_metric.body_battery,
            "stress_level": health_metric.stress_level,
            "steps": health_metric.steps,
            "source": health_metric.source,
            "data_quality": health_metric.data_quality
        }
    
    def generate_personalized_training_plan(
        self,
        user: models.User,
        recent_workouts: List[models.Workout],
        plan_request: Any,
        db: Session = None
    ) -> Dict[str, Any]:
        """Generate highly personalized multi-week training plan.
        
        Args:
            user: User for whom to generate plan
            recent_workouts: Recent workout history for context
            plan_request: TrainingPlanRequest with all personalization parameters
            db: Database session
            
        Returns:
            Dict with complete training plan
        """
        from datetime import datetime, timedelta
        
        # Si training_method es "automatic", determinar automáticamente
        training_method = plan_request.training_method
        if training_method == "automatic":
            # Determinar basado en datos del usuario
            # Si tiene muchos entrenamientos con HR, usar HR-based
            recent_with_hr = sum(1 for w in recent_workouts if w.avg_heart_rate)
            if len(recent_workouts) > 0 and recent_with_hr / len(recent_workouts) > 0.7:
                training_method = "heart_rate_based"
            else:
                training_method = "pace_based"
        
        # Calculate plan dates
        start_date = datetime.now()
        # Adjust to next Monday if not already
        days_until_monday = (7 - start_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 0  # Start Monday
        start_date = start_date + timedelta(days=days_until_monday)
        
        end_date = start_date + timedelta(weeks=plan_request.plan_duration_weeks - 1, days=6)
        
        # Build detailed context
        goals_text = ""
        if plan_request.has_target_race and plan_request.target_race:
            race = plan_request.target_race
            goals_text = f"""
OBJETIVO PRINCIPAL - CARRERA OBJETIVO:
- Nombre: {race.race_name}
- Fecha: {race.race_date}
- Distancia: {race.distance_km} km
- Tiempo objetivo: {race.target_time_minutes} minutos ({race.target_time_minutes/60:.1f} horas)
- Ritmo objetivo: {race.target_pace_min_per_km:.1f} min/km
"""
        else:
            goals_text = f"Objetivo general: {plan_request.general_goal}"
        
        # Build strength training context
        strength_context = ""
        if plan_request.include_strength_training:
            strength_context = f"""
ENTRENAMIENTOS DE FUERZA:
- Incluir: Sí
- Ubicación: {plan_request.strength_location}
- Frecuencia: 2-3 sesiones por semana
- Enfoque: Core, fortaleza de piernas, prevención de lesiones
"""
        
        # Build training method context
        method_label = "Ritmo (min/km)" if training_method == "pace_based" else "Frecuencia Cardíaca (Zonas HR)"
        method_context = f"""
MÉTODO DE PLANIFICACIÓN:
- Planificación por: {method_label}
"""
        
        # Get recent data for context
        recent_distance_km = sum(w.distance_meters / 1000 for w in recent_workouts[:10])
        recent_weeks_with_data = min(len(set(w.start_time.isocalendar()[1] for w in recent_workouts[-20:])), 10) or 1
        avg_weekly_km = recent_distance_km / recent_weeks_with_data if recent_weeks_with_data > 0 else 20
        
        user_prompt = f"""Genera un plan de entrenamiento de running DETALLADO y PERSONALIZADO.

{goals_text}

PREFERENCIAS DEL ATLETA:
- Prioridad de entrenamiento: {plan_request.priority}
- Días disponibles por semana: {plan_request.training_days_per_week}
- Día preferido para tirada larga: {plan_request.preferred_long_run_day}
- Duración del plan: {plan_request.plan_duration_weeks} semanas
- Enfoque de recuperación: {plan_request.recovery_focus}
{strength_context}
- Incluir cross-training: {'Sí' if plan_request.include_cross_training else 'No'}
{method_context}
- Consideraciones por lesión: {plan_request.injury_considerations or 'Ninguna'}

CONTEXTO DEL ATLETA:
- Volumen actual: {avg_weekly_km:.1f} km/semana
- Entrenamientos recientes: {len(recent_workouts)} en las últimas semanas

INSTRUCCIONES CRÍTICAS:
1. Crea un plan de {plan_request.plan_duration_weeks} semanas, comenzando el {start_date.strftime('%d/%m/%Y')}
2. Cada semana debe tener exactamente {plan_request.training_days_per_week} días de entrenamiento
3. El día de tirada larga debe ser {plan_request.preferred_long_run_day}
4. Aumenta el volumen gradualmente (máximo 10% por semana)
5. Varía las intensidades según la prioridad ({plan_request.priority})
6. Incluye tipos: Easy Run, Tempo Run, Speed/Intervals, Long Run, Recovery
{f'7. Los entrenamientos de fuerza deben ser 2x/semana en {plan_request.strength_location}' if plan_request.include_strength_training else ''}
8. Respeta el enfoque de recuperación ({plan_request.recovery_focus})
9. **IMPORTANTE - MÉTODO DE ENTRENAMIENTO**: 
   - Si el método es "pace_based": Especifica SOLO ritmo (pace_min_per_km) y distancia. Omite heart_rate_zone.
   - Si el método es "heart_rate_based": Especifica SOLO zona HR (heart_rate_zone 1-5) y duración. Omite pace_min_per_km y distancia.
   - El método actual es: {training_method}

FORMATO REQUERIDO (JSON structure - ADAPTA SEGÚN EL MÉTODO):
{{
  "id": "plan_YYYYMMDD_HHMMSS",
  "name": "Plan de {plan_request.plan_duration_weeks} semanas - {plan_request.general_goal}",
  "start_date": "{start_date.strftime('%Y-%m-%d')}",
  "end_date": "{end_date.strftime('%Y-%m-%d')}",
  "training_method": "{training_method}",
  "weeks": [
    {{
      "week_number": 1,
      "days": [
        {{
          "day": "Lunes",
          "type": "Easy Run",
          "description": "Carrera suave de calentamiento"{"," if training_method == "pace_based" else ""}
{f'"distance_km": 7.5,' if training_method == "pace_based" else ""}
{f'"pace_min_per_km": 6.2,' if training_method == "pace_based" else ""}
{f'"duration_minutes": 45' if training_method == "pace_based" else '"heart_rate_zone": 2, "duration_minutes": 45'}
        }}
      ],
      "total_km": 45.0
    }}
  ]
}}

Retorna SOLO el JSON válido, sin explicaciones adicionales."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un entrenador de running profesional. Genera planes de entrenamiento detallados y personalizados basados en los parámetros del atleta. Retorna JSON válido."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Parse response
            plan_text = completion.choices[0].message.content
            
            # Try to extract JSON if embedded in text
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', plan_text)
            if json_match:
                plan_json = json.loads(json_match.group())
            else:
                plan_json = json.loads(plan_text)
            
            return plan_json
            
        except Exception as e:
            # Fallback: generate a basic plan structure
            logger.error(f"Error generating personalized plan: {str(e)}")
            return self._generate_fallback_plan(
                plan_request,
                start_date,
                end_date,
                training_method
            )
    
    def _generate_fallback_plan(
        self,
        plan_request: Any,
        start_date: datetime,
        end_date: datetime,
        training_method: str = "pace_based"
    ) -> Dict[str, Any]:
        """Generate a basic fallback plan when AI generation fails."""
        from datetime import timedelta
        
        weeks = []
        current_date = start_date
        base_distance = 40 if plan_request.general_goal in ['marathon', 'build_endurance'] else 25
        
        for week_num in range(1, plan_request.plan_duration_weeks + 1):
            week_progression = 1 + ((week_num - 1) * 0.05)  # 5% increase per week
            days = []
            total_km = 0
            
            training_days = [
                ("Easy Run", "Carrera suave aeróbica", 8 * week_progression, 6.5),
                ("Speed Work", "Trabajo de velocidad", 6 * week_progression, 5.8),
                ("Tempo Run", "Carrera de tempo", 7 * week_progression, 6.0),
            ]
            
            if plan_request.training_days_per_week >= 4:
                training_days.append(("Long Run", "Tirada larga", 12 * week_progression, 6.8))
            if plan_request.training_days_per_week >= 5:
                training_days.append(("Recovery", "Carrera de recuperación", 5 * week_progression, 7.0))
            
            for day_idx, (day_type, description, distance, pace) in enumerate(training_days[:plan_request.training_days_per_week]):
                day_date = current_date + timedelta(days=day_idx)
                day_name = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][day_idx % 7]
                
                days.append({
                    "day": day_name,
                    "type": day_type,
                    "description": description,
                    "distance_km": round(distance, 1),
                    "pace_min_per_km": round(pace, 1),
                    "heart_rate_zone": 2 if "Easy" in day_type or "Recovery" in day_type else 3 if "Tempo" in day_type else 4,
                    "duration_minutes": int(distance * pace)
                })
                total_km += distance
            
            weeks.append({
                "week_number": week_num,
                "days": days,
                "total_km": round(total_km, 1)
            })
            
            current_date += timedelta(days=7)
        
        return {
            "id": f"plan_{start_date.strftime('%Y%m%d_%H%M%S')}",
            "name": f"Plan de {plan_request.plan_duration_weeks} semanas - {plan_request.general_goal}",
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "weeks": weeks,
            "general_goal": plan_request.general_goal,
            "priority": plan_request.priority,
            "training_days_per_week": plan_request.training_days_per_week,
            "plan_duration_weeks": plan_request.plan_duration_weeks,
            "total_volume_km": round(sum(w["total_km"] for w in weeks), 1),
            "max_weekly_distance_km": round(max(w["total_km"] for w in weeks), 1)
        }


# Lazy-loaded singleton instance (instantiated on first use)
_coach_service_instance = None

def get_coach_service() -> "CoachService":
    """Get or create the coach service singleton."""
    global _coach_service_instance
    if _coach_service_instance is None:
        _coach_service_instance = CoachService()
    return _coach_service_instance

# Backwards compatibility alias
@property
def coach_service():
    """Deprecated: Use get_coach_service() instead."""
    return get_coach_service()

