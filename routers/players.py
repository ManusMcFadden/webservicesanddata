from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import get_db

router = APIRouter(
    prefix="/players",
    tags=["players"]
)

@router.get("/", response_model=List[schemas.Player])
def read_players(skip: int = 0, limit: int = 100, ioc: str = None, db: Session = Depends(get_db)):
    '''Retrieve a list of players with optional pagination and filtering by IOC country code.'''
    return crud.get_players(db, skip=skip, limit=limit, ioc=ioc)

@router.get("/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db)):
    '''Retrieve a single player by their unique ID.'''
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# UPDATE: PATCH /players/{id}
@router.patch("/{player_id}", response_model=schemas.Player)
def update_existing_player(player_id: int, player_update: schemas.PlayerUpdate, db: Session = Depends(get_db)):
    '''Update an existing player's information. Only the fields provided in the request will be updated.'''
    db_player = crud.update_player(db, player_id=player_id, player_update=player_update)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# DELETE: DELETE /players/{id}
@router.delete("/{player_id}", response_model=schemas.DeleteResponse)
def delete_existing_player(player_id: int, db: Session = Depends(get_db)):
    '''Delete a player by their unique ID. Returns a confirmation message if successful.'''
    success = crud.delete_player(db, player_id=player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully", "player_id": player_id}

# --- ADVANCED ENDPOINTS ---

@router.get("/{player_id}/matches", response_model=List[schemas.Match])
def read_player_matches(player_id: int, db: Session = Depends(get_db)):
    '''Retrieve all matches involving a specific player, either as winner or loser.'''
    return crud.get_player_matches(db, player_id=player_id)

@router.get("/{player_id}/rankings", response_model=List[schemas.Ranking])
def read_player_rankings(player_id: int, db: Session = Depends(get_db)):
    '''Retrieve all rankings for a specific player.'''
    return crud.get_player_rankings(db, player_id=player_id)

@router.get("/stats/top-by-surface", response_model=List[schemas.PlayerSurfaceStat])
def read_top_players(
    surface: schemas.SurfaceType = schemas.SurfaceType.clay, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    Returns the top players ranked by win rate on a specific surface.
    The surface is validated against ATP standard types.
    """
    # .value gets the string "Clay", "Grass", etc. from the Enum
    return crud.get_top_players_by_surface(db, surface=surface.value, limit=limit)

@router.get("/stats/service-kings", response_model=List[schemas.ServiceKing])
def read_service_kings(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a leaderboard of the best servers (highest average aces per win).
    Only includes players with at least 10 recorded wins.
    """
    stats = crud.get_service_kings(db, limit=limit)
    if not stats:
        raise HTTPException(status_code=404, detail="No service statistics found.")
    return stats

@router.get("/stats/giant-slayers", response_model=List[schemas.GiantSlayer])
def read_giant_slayers(min_gap: int = 50, limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns a leaderboard of players with the most 'upset' wins.
    An upset is defined by the gap between the winner's rank and the loser's rank.
    """
    return crud.get_top_giant_slayers(db, min_rank_gap=min_gap, limit=limit)