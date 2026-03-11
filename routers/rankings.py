from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas
from database import get_db
from typing import Optional

router = APIRouter(prefix="/rankings", tags=["rankings"])

# --- READ (List) ---
@router.get("/", response_model=List[schemas.Ranking])
def read_rankings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of rankings with pagination."""
    return crud.get_rankings(db, skip=skip, limit=limit)

# --- ADVANCED ENDPOINTS ---
@router.get("/stats/hall-of-fame", response_model=List[schemas.HallOfFamer])
def read_hall_of_fame(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns an all-time leaderboard of players who have spent the most 
    weeks ranked as World Number 1.
    """
    stats = crud.get_hall_of_fame(db, limit=limit)
    if not stats:
        raise HTTPException(status_code=404, detail="No ranking data found.")
    return stats

# --- READ (Single) ---
@router.get("/{ranking_date}/{player_id}", response_model=schemas.Ranking)
def read_ranking(ranking_date: int, player_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific ranking entry by date and player ID."""
    db_rank = crud.get_ranking(db, ranking_date=ranking_date, player_id=player_id)
    if db_rank is None:
        raise HTTPException(status_code=404, detail="Ranking entry not found")
    return db_rank

# --- UPDATE (PATCH) ---
@router.patch("/{ranking_date}/{player_id}", response_model=schemas.Ranking)
def update_ranking(ranking_date: int, player_id: int, ranking_update: schemas.RankingUpdate, db: Session = Depends(get_db)):
    """Update a specific ranking entry (e.g., change rank or points)."""
    db_rank = crud.update_ranking(db, ranking_date=ranking_date, player_id=player_id, rank_update=ranking_update)
    if db_rank is None:
        raise HTTPException(status_code=404, detail="Ranking entry not found")
    return db_rank

# --- CREATE (POST) ---
@router.post("/", response_model=schemas.Ranking, status_code=201)
def create_ranking(ranking: schemas.RankingCreate, db: Session = Depends(get_db)):
    return crud.create_ranking(db=db, ranking=ranking)

# --- DELETE ---
@router.delete("/{ranking_date}/{player_id}")
def delete_ranking(ranking_date: int, player_id: int, db: Session = Depends(get_db)):
    if not crud.delete_ranking(db, ranking_date, player_id):
        raise HTTPException(status_code=404, detail="Ranking entry not found")
    return {"message": "Ranking deleted"}

