from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/players",
    tags=["players"]
)

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

@router.get("/", response_model=List[schemas.Player], responses={**COMMON_ERRORS})
def read_players(skip: int = 0, limit: int = 100, ioc: str = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Retrieve a list of players with optional pagination and filtering by IOC country code.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view players.")
    db_players = crud.get_players(db, skip=skip, limit=limit, ioc=ioc)
    if not db_players:
        raise HTTPException(status_code=404, detail="No players found.")
    return db_players

@router.get("/{player_id}", response_model=schemas.Player, responses={**COMMON_ERRORS})
def read_player(player_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Retrieve a single player by their unique ID.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view this player.")
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# UPDATE: PATCH /players/{id}
@router.patch("/{player_id}", response_model=schemas.Player, responses={**COMMON_ERRORS})
def update_existing_player(player_id: int, player_update: schemas.PlayerUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Update an existing player's information. Only the fields provided in the request will be updated.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to update a player.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can update player information.")
    db_player = crud.update_player(db, player_id=player_id, player_update=player_update)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# DELETE: DELETE /players/{id}
@router.delete("/{player_id}", response_model=schemas.DeleteResponse, responses={**COMMON_ERRORS})
def delete_existing_player(player_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Delete a player by their unique ID. Returns a confirmation message if successful.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to delete a player.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can delete players.")
    success = crud.delete_player(db, player_id=player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully", "player_id": player_id}

@router.post("/", response_model=schemas.Player, status_code=201, responses={**COMMON_ERRORS})
def create_new_player(player: schemas.PlayerCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Create a new player with the provided information.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to create a player.")
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden: Only admins can create players.")
    db_player = crud.create_player(db=db, player=player)
    if db_player is None:
        raise HTTPException(status_code=400, detail="Failed to create player. Please check the input data.")
    return db_player

@router.get("/player-by-name/", response_model=schemas.Player, responses={**COMMON_ERRORS})
def read_player_by_name(name_first: str, name_last: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Retrieve a player by their first and last name.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view player information.")
    db_player = crud.get_player_by_name(db, name_first=name_first, name_last=name_last)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

# --- ADVANCED ENDPOINTS ---

@router.get("/{player_id}/matches", response_model=List[schemas.Match], responses={**COMMON_ERRORS})
def read_player_matches(player_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Retrieve all matches involving a specific player, either as winner or loser.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view player matches.")
    db_matches = crud.get_player_matches(db, player_id=player_id)
    if not db_matches:
        raise HTTPException(status_code=404, detail="No matches found for this player.")
    return db_matches

@router.get("/{player_id}/rankings", response_model=List[schemas.Ranking], responses={**COMMON_ERRORS})
def read_player_rankings(player_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    '''Retrieve all rankings for a specific player.'''
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view player rankings.")
    db_rankings = crud.get_player_rankings(db, player_id=player_id)
    if not db_rankings:
        raise HTTPException(status_code=404, detail="No rankings found for this player.")
    return db_rankings

@router.get("/stats/top-by-surface", response_model=List[schemas.PlayerSurfaceStat], responses={**COMMON_ERRORS})
def read_top_players(
    surface: schemas.SurfaceType = schemas.SurfaceType.clay, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Returns the top players ranked by win rate on a specific surface.
    The surface is validated against ATP standard types.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view player statistics.")
    # .value gets the string "Clay", "Grass", etc. from the Enum
    db_players = crud.get_top_players_by_surface(db, surface=surface.value, limit=limit)
    if not db_players:
        raise HTTPException(status_code=404, detail="No players found for the specified surface.")
    return db_players

@router.get("/stats/service-kings", response_model=List[schemas.ServiceKing], responses={**COMMON_ERRORS})
def read_service_kings(limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Get a leaderboard of the best servers (highest average aces per win).
    Only includes players with at least 10 recorded wins.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view service statistics.")
    stats = crud.get_service_kings(db, limit=limit)
    if not stats:
        raise HTTPException(status_code=404, detail="No service statistics found.")
    return stats

@router.get("/stats/giant-slayers", response_model=List[schemas.GiantSlayer], responses={**COMMON_ERRORS})
def read_giant_slayers(min_gap: int = 50, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Returns a leaderboard of players with the most 'upset' wins.
    An upset is defined by the gap between the winner's rank and the loser's rank.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized: You must be logged in to view giant slayer statistics.")
    db_giant_slayers = crud.get_top_giant_slayers(db, min_rank_gap=min_gap, limit=limit)
    if not db_giant_slayers:
        raise HTTPException(status_code=404, detail="No giant slayers found.")
    return db_giant_slayers