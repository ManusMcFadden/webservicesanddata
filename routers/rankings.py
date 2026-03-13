from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas, models, auth
from database import get_db
from typing import Optional

router = APIRouter(prefix="/rankings", tags=["rankings"])

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
@router.get("/", response_model=List[schemas.Ranking], responses={**COMMON_ERRORS})
def read_rankings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Retrieve a list of rankings with pagination."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view rankings.")
    db_rankings = crud.get_rankings(db, skip=skip, limit=limit)
    if not db_rankings:
        raise HTTPException(status_code=404, detail="No rankings found.")
    return db_rankings

# --- ADVANCED ENDPOINTS ---
@router.get("/stats/hall-of-fame", response_model=List[schemas.HallOfFamer], responses={**COMMON_ERRORS})
def read_hall_of_fame(limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Returns an all-time leaderboard of players who have spent the most 
    weeks ranked as World Number 1.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view hall of fame statistics.")
    stats = crud.get_hall_of_fame(db, limit=limit)
    if not stats:
        raise HTTPException(status_code=404, detail="No ranking data found.")
    return stats

# --- READ (Single) ---
@router.get("/{ranking_date}/{player_id}", response_model=schemas.Ranking, responses={**COMMON_ERRORS})
def read_ranking(ranking_date: int, player_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Retrieve a specific ranking entry by date and player ID."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view ranking entries.")
    db_rank = crud.get_ranking(db, ranking_date=ranking_date, player_id=player_id)
    if db_rank is None:
        raise HTTPException(status_code=404, detail="Ranking entry not found")
    return db_rank

# --- UPDATE (PATCH) ---
@router.patch("/{ranking_date}/{player_id}", response_model=schemas.Ranking, responses={**COMMON_ERRORS})
def update_ranking(ranking_date: int, player_id: int, ranking_update: schemas.RankingUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Update a specific ranking entry (e.g., change rank or points)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to update ranking entries.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can update ranking entries.")
    db_rank = crud.update_ranking(db, ranking_date=ranking_date, player_id=player_id, rank_update=ranking_update)
    if db_rank is None:
        raise HTTPException(status_code=404, detail="Ranking entry not found")
    return db_rank

# --- CREATE (POST) ---
@router.post("/", response_model=schemas.Ranking, status_code=201, responses={**COMMON_ERRORS})
def create_ranking(ranking: schemas.RankingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Create a new ranking entry for a player on a specific date."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to create ranking entries.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can create ranking entries.")
    db_rank = crud.create_ranking(db=db, ranking=ranking)
    if db_rank is None:
        raise HTTPException(status_code=400, detail="Failed to create ranking. Please check the input data.")
    return db_rank

# --- DELETE ---
@router.delete("/{ranking_date}/{player_id}", response_model=schemas.DeleteResponse, responses={**COMMON_ERRORS})
def delete_ranking(ranking_date: int, player_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Delete a specific ranking entry by date and player ID."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to delete ranking entries.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can delete ranking entries.")
    if not crud.delete_ranking(db, ranking_date, player_id):
        raise HTTPException(status_code=404, detail="Ranking entry not found")
    return {"message": "Ranking deleted"}

