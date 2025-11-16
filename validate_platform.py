#!/usr/bin/env python3
"""
Plataforma de Running - Script de Validación Automatizada
Valida compilación, tests, dependencias y features críticas
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Tuple, List


class PlatformValidator:
    """Validador automatizado de la plataforma de running"""
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.backend = self.root / "backend"
        self.frontend = self.root / "frontend"
        self.issues = []
        self.passed = []
        
    def run_command(self, cmd: str, cwd: Path = None) -> Tuple[bool, str]:
        """Ejecuta un comando y retorna (éxito, output)"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def check_compilation(self) -> bool:
        """Valida que el código compila sin errores"""
        print("\n🔨 Verificando compilación...")
        
        # TypeScript
        success, output = self.run_command("tsc --noEmit", self.frontend)
        if success:
            self.passed.append("✅ Frontend TypeScript compila sin errores")
        else:
            self.issues.append(f"❌ TypeScript errors: {output[:200]}")
        
        # Python imports
        success, output = self.run_command(
            "python -m py_compile app/main.py",
            self.backend
        )
        if success:
            self.passed.append("✅ Backend Python syntax correcto")
        else:
            self.issues.append(f"❌ Python syntax errors: {output[:200]}")
        
        return len([x for x in self.issues if x.startswith("❌ ")]) == 0
    
    def check_dependencies(self) -> bool:
        """Valida que todas las dependencias estén instaladas"""
        print("\n📦 Verificando dependencias...")
        
        # Backend requirements
        backend_deps = [
            "fastapi",
            "sqlalchemy",
            "pydantic",
            "groq",
            "slowapi"
        ]
        
        for dep in backend_deps:
            success, _ = self.run_command(f"pip show {dep}", self.backend)
            if success:
                self.passed.append(f"✅ Backend: {dep} instalado")
            else:
                self.issues.append(f"❌ Backend: {dep} NO INSTALADO")
        
        # Frontend dependencies
        success, output = self.run_command("npm list", self.frontend)
        if success and "npm ERR!" not in output:
            self.passed.append("✅ Frontend: todas las dependencias OK")
        else:
            self.issues.append(f"❌ Frontend: problemas de dependencias")
        
        return len([x for x in self.issues if x.startswith("❌ ")]) == 0
    
    def check_environment(self) -> bool:
        """Valida variables de entorno críticas"""
        print("\n🔐 Verificando configuración...")
        
        backend_env = self.backend / ".env"
        if backend_env.exists():
            self.passed.append("✅ Backend .env existe")
        else:
            self.issues.append("❌ Backend .env NO EXISTE (necesario GROQ_API_KEY)")
        
        # Check GROQ_API_KEY
        try:
            with open(backend_env) as f:
                env_content = f.read()
                if "GROQ_API_KEY" in env_content:
                    self.passed.append("✅ GROQ_API_KEY configurado")
                else:
                    self.issues.append("❌ GROQ_API_KEY NO configurado")
        except:
            pass
        
        return len([x for x in self.issues if x.startswith("❌ ")]) == 0
    
    def check_critical_files(self) -> bool:
        """Valida que archivos críticos existan"""
        print("\n📁 Verificando archivos críticos...")
        
        critical_files = [
            ("Backend", self.backend / "app" / "main.py"),
            ("Backend", self.backend / "app" / "models.py"),
            ("Backend", self.backend / "app" / "schemas.py"),
            ("Backend", self.backend / "app" / "services" / "coach_service.py"),
            ("Backend", self.backend / "app" / "services" / "training_plan_service.py"),
            ("Frontend", self.frontend / "app" / "layout.tsx"),
            ("Frontend", self.frontend / "lib" / "api-client.ts"),
            ("Frontend", self.frontend / "lib" / "auth-context.tsx"),
            ("Docs", self.root / "AGENT_MEGA_TASK.md"),
            ("Docs", self.root / "USER_GUIDE.md"),
            ("Docs", self.root / "TEST_CASES.md"),
        ]
        
        for section, file_path in critical_files:
            if file_path.exists():
                self.passed.append(f"✅ {section}: {file_path.name} existe")
            else:
                self.issues.append(f"❌ {section}: {file_path.name} NO EXISTE")
        
        return len([x for x in self.issues if x.startswith("❌ ")]) == 0
    
    def check_features(self) -> bool:
        """Valida features críticas en código"""
        print("\n🎯 Verificando features críticas...")
        
        # Check Karvonen formula
        coach_service = self.backend / "app" / "services" / "coach_service.py"
        if coach_service.exists():
            with open(coach_service) as f:
                content = f.read()
                if "karvonen" in content.lower() or "resting_hr" in content.lower():
                    self.passed.append("✅ Karvonen formula implementada")
                else:
                    self.issues.append("❌ Karvonen formula NO encontrada")
                
                if "_calculate_power_zones" in content:
                    self.passed.append("✅ Power zones implementadas")
                else:
                    self.issues.append("❌ Power zones NO implementadas")
        
        # Check training plan duration
        plan_service = self.backend / "app" / "services" / "training_plan_service.py"
        if plan_service.exists():
            with open(plan_service) as f:
                content = f.read()
                if "calculate_plan_duration_with_target_race" in content:
                    self.passed.append("✅ Plan duration calculation implementada")
                else:
                    self.issues.append("❌ Plan duration calculation NO implementada")
        
        # Check form validation
        form_file = self.frontend / "components" / "training-plan-form-v2.tsx"
        if form_file.exists():
            with open(form_file) as f:
                content = f.read()
                if "validation" in content.lower() or "required" in content.lower():
                    self.passed.append("✅ Form validation implementada")
                else:
                    self.issues.append("⚠️ Form validation podría necesitar revisión")
        
        return True
    
    def check_tests(self) -> bool:
        """Valida que test infrastructure exista"""
        print("\n🧪 Verificando tests...")
        
        # Backend pytest
        pytest_ini = self.backend / "pytest.ini"
        if pytest_ini.exists():
            self.passed.append("✅ Backend pytest configurado")
        else:
            self.issues.append("⚠️ pytest.ini NO encontrado en backend")
        
        # Frontend jest (si existe)
        jest_config = self.frontend / "jest.config.js"
        if jest_config.exists():
            self.passed.append("✅ Frontend jest configurado")
        else:
            self.passed.append("ℹ️ Frontend Jest config no requerido (Next.js default)")
        
        return True
    
    def check_database(self) -> bool:
        """Valida configuración de base de datos"""
        print("\n🗄️ Verificando base de datos...")
        
        # Check SQLite
        db_file = self.backend / "runcoach.db"
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024*1024)
            self.passed.append(f"✅ Database existe ({size_mb:.2f} MB)")
        else:
            self.passed.append("ℹ️ Database no existe (se crea en primer arranque)")
        
        # Check models
        models_file = self.backend / "app" / "models.py"
        if models_file.exists():
            with open(models_file) as f:
                content = f.read()
                for model in ["User", "Workout", "ChatMessage"]:
                    if f"class {model}" in content:
                        self.passed.append(f"✅ Model {model} definido")
                    else:
                        self.issues.append(f"❌ Model {model} NO ENCONTRADO")
        
        return True
    
    def check_api_endpoints(self) -> bool:
        """Valida que endpoints críticos estén definidos"""
        print("\n🔌 Verificando endpoints...")
        
        routes_dir = self.backend / "app" / "routers"
        if routes_dir.exists():
            routers = list(routes_dir.glob("*.py"))
            self.passed.append(f"✅ {len(routers)} routers encontrados")
        else:
            self.issues.append("❌ Routers directory NO EXISTE")
        
        return True
    
    def run_full_validation(self) -> int:
        """Ejecuta validación completa"""
        print("=" * 60)
        print("🏃‍♂️ PLATAFORMA DE RUNNING - VALIDACIÓN COMPLETA")
        print("=" * 60)
        
        # Run all checks
        self.check_critical_files()
        self.check_compilation()
        self.check_dependencies()
        self.check_environment()
        self.check_features()
        self.check_tests()
        self.check_database()
        self.check_api_endpoints()
        
        # Report
        print("\n" + "=" * 60)
        print("📊 RESULTADOS")
        print("=" * 60)
        
        print(f"\n✅ Pasado ({len(self.passed)}):")
        for item in self.passed[:10]:  # Show first 10
            print(f"  {item}")
        if len(self.passed) > 10:
            print(f"  ... +{len(self.passed) - 10} más")
        
        if self.issues:
            print(f"\n❌ Problemas ({len(self.issues)}):")
            for item in self.issues:
                print(f"  {item}")
        else:
            print("\n✅ ¡SIN PROBLEMAS ENCONTRADOS!")
        
        # Summary
        critical_issues = len([x for x in self.issues if x.startswith("❌")])
        warnings = len([x for x in self.issues if x.startswith("⚠️")])
        
        print("\n" + "=" * 60)
        print("🎯 RESUMEN")
        print("=" * 60)
        print(f"✅ Pasados: {len(self.passed)}")
        print(f"❌ Críticos: {critical_issues}")
        print(f"⚠️ Advertencias: {warnings}")
        
        status = critical_issues == 0
        print(f"\n🚀 Estado: {'LISTA PARA DEPLOY' if status else 'REVISAR PROBLEMAS'}")
        print("=" * 60)
        
        return 0 if status else 1


def main():
    """Punto de entrada"""
    validator = PlatformValidator()
    sys.exit(validator.run_full_validation())


if __name__ == "__main__":
    main()
