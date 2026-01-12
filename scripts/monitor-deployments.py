#!/usr/bin/env python3
"""
Script de monitoreo de deployments en Vercel y Render.
Verifica el estado de los servicios haciendo health checks HTTP.
"""

import requests
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_service(name: str, url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Verifica el estado de un servicio haciendo una petición HTTP.
    
    Args:
        name: Nombre del servicio
        url: URL del servicio
        timeout: Timeout en segundos
        
    Returns:
        Dict con el estado del servicio
    """
    result = {
        "name": name,
        "url": url,
        "status": "unknown",
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        start_time = datetime.now()
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        
        result["status_code"] = response.status_code
        result["response_time_ms"] = round(response_time, 2)
        
        if response.status_code == 200:
            result["status"] = "healthy"
        elif response.status_code in [301, 302, 307, 308]:
            result["status"] = "redirecting"
        elif response.status_code == 503:
            result["status"] = "unavailable"
        elif response.status_code >= 500:
            result["status"] = "error"
        else:
            result["status"] = "warning"
            
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = f"Timeout after {timeout}s"
    except requests.exceptions.ConnectionError:
        result["status"] = "unreachable"
        result["error"] = "No se pudo conectar al servidor"
    except requests.exceptions.RequestException as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def print_status(result: Dict[str, Any]) -> None:
    """Imprime el estado de un servicio con colores."""
    name = result["name"]
    url = result["url"]
    status = result["status"]
    status_code = result["status_code"]
    response_time = result["response_time_ms"]
    error = result["error"]
    
    # Seleccionar color según el estado
    if status == "healthy":
        color = Colors.GREEN
        icon = "✅"
    elif status == "redirecting":
        color = Colors.YELLOW
        icon = "⚠️"
    elif status in ["unreachable", "timeout", "unavailable", "error"]:
        color = Colors.RED
        icon = "❌"
    else:
        color = Colors.YELLOW
        icon = "⚠️"
    
    print(f"\n{color}{Colors.BOLD}{icon} {name}{Colors.RESET}")
    print(f"  URL: {url}")
    
    if status_code:
        print(f"  Status Code: {status_code}")
    
    if response_time:
        print(f"  Response Time: {response_time}ms")
    
    print(f"  Status: {color}{status.upper()}{Colors.RESET}")
    
    if error:
        print(f"  Error: {Colors.RED}{error}{Colors.RESET}")

def main():
    """Función principal de monitoreo."""
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 Monitoreo de Deployments - RunCoach AI{Colors.RESET}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # URLs de producción (ajustar según tu configuración)
    services = [
        {
            "name": "Frontend (Vercel)",
            "url": "https://plataforma-running.vercel.app"
        },
        # Backend URL - necesitarás actualizar esto con tu URL de Render
        # {
        #     "name": "Backend API (Render)",
        #     "url": "https://tu-backend-url.onrender.com/health"
        # },
    ]
    
    # Si se pasa una URL de backend como argumento, usarla
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
        services.append({
            "name": "Backend API (Render)",
            "url": backend_url.rstrip('/') + "/health"
        })
    
    results = []
    for service in services:
        result = check_service(service["name"], service["url"])
        results.append(result)
        print_status(result)
    
    # Resumen
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}📊 Resumen{Colors.RESET}\n")
    
    healthy_count = sum(1 for r in results if r["status"] == "healthy")
    total_count = len(results)
    
    if healthy_count == total_count:
        print(f"{Colors.GREEN}✅ Todos los servicios están operativos ({healthy_count}/{total_count}){Colors.RESET}")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  Algunos servicios tienen problemas ({healthy_count}/{total_count} operativos){Colors.RESET}")
        failed = [r for r in results if r["status"] != "healthy"]
        for r in failed:
            print(f"  - {Colors.RED}{r['name']}: {r['status']}{Colors.RESET}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Monitoreo interrumpido por el usuario{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.RESET}")
        sys.exit(1)
