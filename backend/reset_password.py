"""Script para resetear contraseña de usuario"""
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

def reset_password(email: str, new_password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ Usuario {email} no encontrado")
            return
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        print(f"✅ Contraseña actualizada para {email}")
        print(f"   Nueva contraseña: {new_password}")
    finally:
        db.close()

if __name__ == "__main__":
    # Cambiar la contraseña aquí
    EMAIL = "guillermomartindeoliva@gmail.com"
    NEW_PASSWORD = "password123"  # Mínimo 8 caracteres
    
    reset_password(EMAIL, NEW_PASSWORD)
