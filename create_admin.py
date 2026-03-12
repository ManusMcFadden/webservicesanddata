from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth

def create_initial_user():
    db = SessionLocal()
    
    # Configuration for your first user
    username = "admin"
    password = "tennis_password_2024"
    
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        print(f"User '{username}' already exists.")
        return

    # Hash the password and save
    hashed_pw = auth.get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed_pw)
    
    db.add(new_user)
    db.commit()
    print(f"Successfully created user: {username}")
    db.close()

if __name__ == "__main__":
    # Create the users table if it doesn't exist yet
    models.Base.metadata.create_all(bind=engine)
    create_initial_user()