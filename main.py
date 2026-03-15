from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from routers import players, matches, rankings
import models, schemas
from database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm
import auth
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import os, uvicorn

# Initialize the FastAPI app
app = FastAPI(
    title="Tennis Statistics API",
    description="""COMP3011 Project: ATP Match and Ranking Data (2020-2024)\n
    ##Authentication\n
    The API uses OAuth2 with JWT tokens for authentication:\n
    * **POST /signup**: Create a new user account with a username and password. Returns user details.\n
    * **POST /login**: Authenticate with username and password. Returns a JWT access token with 'bearer' type.\n
    * **Token Usage**: Include the JWT token in the Authorization header as 'Bearer <token>' when making authenticated requests.\n
    * **Token Security**: Passwords are hashed using industry-standard algorithms before storage. Tokens are signed and expire after a set duration.\n
    \n
    ##Error Handling Standards\n
    The API follows standard HTTP status codes:\n
    * **200 OK**: The request was successful.\n
    * **201 Created**: A new resource was successfully created (e.g., a new player, match, or ranking entry).\n
    * **400 Bad Request**: The request was invalid or cannot be served. This can occur if required fields are missing, data types are incorrect, or if the request body is malformed.\n
    * **401 Unauthorized**: You must be logged in to perform this action. This status is returned when authentication credentials are missing or invalid.\n
    * **403 Forbidden**: You do not have permission to perform this action. This status is returned when the user is authenticated but does not have the necessary permissions (e.g., trying to delete a player without admin rights).\n
    * **404 Not Found**: The requested resource (Player/Match/Rank) was not found. This can happen if you try to access a player, match, or ranking entry that does not exist in the database.\n
    * **422 Unprocessable Entity**: Validation error when the input data is correctly formatted but semantically incorrect (e.g., trying to create a match with non-existent player IDs).\n
    * **500 Internal Server Error**: Something went wrong on our end. This indicates an unexpected error occurred while processing the request.""",
    version="1.0.0"
)

app.include_router(players.router)
app.include_router(matches.router)
app.include_router(rankings.router)

# Create tables in the DB (if they don't exist)
models.Base.metadata.create_all(bind=engine)

# --- PUBLIC: Open to everyone ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Tennis Stats API. Visit /docs for documentation."}

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username exists...
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username, 
        hashed_password=hashed_pw,
        is_admin=False # Hardcoded to False so no one can hack the signup!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

mcp = FastApiMCP(
    app,
    name="Tennis MCP",
    include_operations=["read_matches", "read_match", "create_match", "update_match", "delete_match", "get_head_to_head",
                        "read_players", "read_player", "update_existing_player", "delete_existing_player", "create_new_player", "read_player_by_name", "read_player_matches", "read_player_rankings", "read_top_players", "read_service_kings", "read_giant_slayers",
                        "read_rankings", "read_hall_of_fame", "read_ranking", "update_ranking", "create_ranking", "delete_ranking"],
    headers={"x-mcp-token": "tennis_manager_dev_key_2024"}
)

mcp.mount()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


