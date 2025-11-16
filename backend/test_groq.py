"""
Test script para verificar conexión con Groq API
"""
import os
from groq import Groq

# Cargar API key desde .env
from dotenv import load_dotenv
load_dotenv()

def test_groq_connection():
    """Test básico de conexión con Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "your_groq_api_key_here":
        print("❌ ERROR: GROQ_API_KEY no configurada en .env")
        print("\nPasos para configurar:")
        print("1. Ve a https://console.groq.com/keys")
        print("2. Crea una API key")
        print("3. Copia la key y reemplaza 'your_groq_api_key_here' en .env")
        return False
    
    try:
        client = Groq(api_key=api_key)
        
        # Test simple con modelo actualizado
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modelo actualizado
            messages=[
                {
                    "role": "system",
                    "content": "Eres un coach de running profesional y motivador."
                },
                {
                    "role": "user",
                    "content": "Di hola y preséntate en una línea."
                }
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        response = completion.choices[0].message.content
        print("✅ Conexión exitosa con Groq!")
        print(f"\n🤖 Coach AI dice: {response}")
        print(f"\n📊 Tokens usados: {completion.usage.total_tokens}")
        print(f"⏱️  Tiempo: {completion.usage.completion_time:.2f}s" if hasattr(completion.usage, 'completion_time') else "")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con Groq: {e}")
        return False


if __name__ == "__main__":
    test_groq_connection()
