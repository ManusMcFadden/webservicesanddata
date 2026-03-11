from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from routers import players, matches, rankings
import models, schemas
from database import engine, get_db

# Initialize the FastAPI app
app = FastAPI(
    title="Tennis Statistics API",
    description="COMP3011 Project: ATP Match and Ranking Data (2020-2024)",
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


