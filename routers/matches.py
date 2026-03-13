from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas, models, auth
from database import get_db

router = APIRouter(prefix="/matches", tags=["matches"])

COMMON_ERRORS = {
    200: {"description": "Successful operation."},
    201: {"description": "Resource created successfully."},
    400: {"description": "Bad Request: The request was invalid or cannot be served."},
    401: {"description": "Unauthorized: You must be logged in to perform this action."},
    403: {"description": "Forbidden: You do not have permission to perform this action."},
    404: {"description": "The requested resource (Player/Match/Rank) was not found."},
    422: {"description": "Validation Error: One or more parameters are incorrectly formatted."},
    500: {"description": "Internal Server Error: Something went wrong on our end."}
}

# --- READ (List) ---
@router.get("/", response_model=List[schemas.Match], responses={**COMMON_ERRORS})
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Retrieve a list of matches with pagination."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view matches.")
    db_matches = crud.get_matches(db, skip=skip, limit=limit)
    if not db_matches:
        raise HTTPException(status_code=404, detail="No matches found.")
    return db_matches

# --- READ (Single) ---
@router.get("/{tourney_id}/{match_num}", response_model=schemas.Match, responses={**COMMON_ERRORS})
def read_match(tourney_id: str, match_num: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Retrieve a specific match using its tournament ID and match number."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view this match.")
    db_match = crud.get_match(db, tourney_id=tourney_id, match_num=match_num)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

# --- CREATE (POST) ---
@router.post("/", response_model=schemas.Match, status_code=201, responses={**COMMON_ERRORS})
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Add a new match to the database."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to create a match.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can create matches.")
    db_match = crud.create_match(db=db, match=match)
    if db_match is None:
        raise HTTPException(status_code=400, detail="Failed to create match. Please check the input data.")
    return db_match

# --- UPDATE (PATCH) ---
@router.patch("/{tourney_id}/{match_num}", response_model=schemas.Match, responses={**COMMON_ERRORS})
def update_match(tourney_id: str, match_num: int, match_update: schemas.MatchUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Update specific fields of an existing match (e.g., score or duration)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to update a match.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can update matches.")
    db_match = crud.update_match(db, tourney_id=tourney_id, match_num=match_num, match_update=match_update)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

# --- DELETE ---
@router.delete("/{tourney_id}/{match_num}", response_model=schemas.DeleteResponse, responses={**COMMON_ERRORS})
def delete_match(tourney_id: str, match_num: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Remove a match from the database."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to delete a match.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can delete matches.")
    if not crud.delete_match(db, tourney_id, match_num):
        raise HTTPException(status_code=404, detail="Match not found")
    return {"message": "Match deleted"}

# --- ADVANCED ENDPOINTS ---
@router.get("/h2h/{p1_id}/{p2_id}", response_model=schemas.H2HStat, responses={**COMMON_ERRORS})
def get_head_to_head(p1_id: int, p2_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Retrieve the head-to-head match history and win statistics between two specific players.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view head-to-head stats.")
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
