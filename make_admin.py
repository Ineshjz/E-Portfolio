from sqlmodel import Session, create_engine, select
from main import AppUser

sqlite_url = "sqlite:///test_database.db"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

email = "admin@test.fr"

with Session(engine) as session:
    user = session.exec(select(AppUser).where(AppUser.email == email)).first()

    if user:
        user.role = "admin"
        session.add(user)
        session.commit()
        print(f"{email} est maintenant admin.")
    else:
        print("Utilisateur introuvable.")
