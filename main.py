from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from routers import players, matches, rankings
import models, schemas
from database import engine, get_db

# Initialize the FastAPI app
app = FastAPI(
    title="Tennis Statistics API",
    description="""COMP3011 Project: ATP Match and Ranking Data (2020-2024) 
    ##Error Handling Standards
    The API follows standard HTTP status codes:
    * **200 OK**: The request was successful.
    * **201 Created**: A new resource was successfully created (e.g., a new player, match, or ranking entry).
    * **400 Bad Request**: The request was invalid or cannot be served. This can occur if required fields are missing, data types are incorrect, or if the request body is malformed.
    * **404 Not Found**: The requested resource (Player/Match/Rank) was not found. This can happen if you try to access a player, match, or ranking entry that does not exist in the database.
    * **422 Unprocessable Entity**: Validation error when the input data is correctly formatted but semantically incorrect (e.g., trying to create a match with non-existent player IDs).
    * **500 Internal Server Error**: Something went wrong on our end. This indicates an unexpected error occurred while processing the request.""",
    version="1.0.0"
)

app.include_router(players.router)
app.include_router(matches.router)
app.include_router(rankings.router)

# Create tables in the DB (if they don't exist)
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Tennis Stats API. Visit /docs for documentation."}


