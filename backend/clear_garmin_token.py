from app.database import SessionLocal
from app.models import User


def clear_garmin(user_email: str = 'guillermomartindeoliva@gmail.com'):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            print('User not found')
            return
        user.garmin_token = None
        user.garmin_email = None
        user.garmin_connected_at = None
        db.commit()
        print('Garmin credentials cleared for', user_email)
    finally:
        db.close()

if __name__ == '__main__':
    clear_garmin()
