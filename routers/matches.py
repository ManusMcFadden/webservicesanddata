from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas
from database import get_db

router = APIRouter(prefix="/matches", tags=["matches"])

# --- READ (List) ---
@router.get("/", response_model=List[schemas.Match])
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of matches with pagination."""
    return crud.get_matches(db, skip=skip, limit=limit)

# --- READ (Single) ---
@router.get("/{tourney_id}/{match_num}", response_model=schemas.Match)
def read_match(tourney_id: str, match_num: int, db: Session = Depends(get_db)):
    """Retrieve a specific match using its tournament ID and match number."""
    db_match = crud.get_match(db, tourney_id=tourney_id, match_num=match_num)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

# --- CREATE (POST) ---
@router.post("/", response_model=schemas.Match, status_code=201)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    """Add a new match to the database."""
    return crud.create_match(db=db, match=match)

# --- UPDATE (PATCH) ---
@router.patch("/{tourney_id}/{match_num}", response_model=schemas.Match)
def update_match(tourney_id: str, match_num: int, match_update: schemas.MatchUpdate, db: Session = Depends(get_db)):
    """Update specific fields of an existing match (e.g., score or duration)."""
    db_match = crud.update_match(db, tourney_id=tourney_id, match_num=match_num, match_update=match_update)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

# --- DELETE ---
@router.delete("/{tourney_id}/{match_num}")
def delete_match(tourney_id: str, match_num: int, db: Session = Depends(get_db)):
    """Remove a match from the database."""
    if not crud.delete_match(db, tourney_id, match_num):
        raise HTTPException(status_code=404, detail="Match not found")
    return {"message": "Match deleted"}

# --- ADVANCED ENDPOINTS ---
@router.get("/h2h/{p1_id}/{p2_id}", response_model=schemas.H2HStat)
def get_head_to_head(p1_id: int, p2_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the head-to-head match history and win statistics between two specific players.
    """
    # 1. Validation step: Check if both players exist
    player1 = crud.get_player(db, player_id=p1_id)
    player2 = crud.get_player(db, player_id=p2_id)
    
    if not player1 or not player2:
        raise HTTPException(status_code=404, detail="One or both players not found in the database.")
        
    # 2. Fetch the data
    h2h_data = crud.get_h2h_matches(db, p1_id=p1_id, p2_id=p2_id)
    
    # 3. Optional: Handle the case where they exist but never played each other
    if h2h_data["total_matches"] == 0:
        raise HTTPException(status_code=404, detail="These players have never played against each other.")
        
    return h2h_data
