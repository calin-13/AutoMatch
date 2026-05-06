"""
Promoveaza un utilizator existent la rol admin.
Folosire: python create_admin.py <email>
"""
import sys
from config import SessionLocal
from models.database import User


def promote(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"EROARE: utilizatorul cu email '{email}' nu exista")
            sys.exit(1)
        if user.role == "admin":
            print(f"OK: {user.username} ({email}) este deja admin")
            return
        user.role = "admin"
        db.commit()
        print(f"OK: {user.username} ({email}) este acum ADMIN")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Folosire: python create_admin.py <email>")
        sys.exit(1)
    promote(sys.argv[1])
