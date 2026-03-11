from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class SurfaceType(str, Enum):
    clay = "Clay"
    grass = "Grass"
    hard = "Hard"

# --- PLAYER SCHEMAS ---
class PlayerBase(BaseModel):
    name_first: str
    name_last: str
    hand: Optional[str] = None
    dob: Optional[int] = None
    ioc: str
    height: Optional[float] = None

class PlayerCreate(PlayerBase):
    player_id: int  # Required for manual creation since it's our PK

class Player(PlayerBase):
    player_id: int
    wikidata_id: Optional[str] = None

    class Config:
        from_attributes = True  # Allows Pydantic to read data from SQLAlchemy models

class PlayerUpdate(BaseModel):
    name_first: Optional[str] = None
    name_last: Optional[str] = None
    hand: Optional[str] = None
    height: Optional[float] = None
    ioc: Optional[str] = None

# --- RANKING SCHEMAS ---
class RankingBase(BaseModel):
    ranking_date: int
    rank: int
    points: Optional[int] = None

class Ranking(RankingBase):
    player: int  # This keeps the ID
    
    # This adds the full player object (name, hand, ioc, etc.)
    # Note: Make sure the Player schema is defined above this class!
    player_details: Optional[Player] = None 

    class Config:
        from_attributes = True

class RankingCreate(RankingBase):
    player: int

class RankingUpdate(BaseModel):
    rank: Optional[int] = None
    points: Optional[int] = None

# --- MATCH SCHEMAS ---

class MatchBase(BaseModel):
    tourney_id: str
    match_num: int
    tourney_name: Optional[str] = None
    surface: Optional[str] = None
    draw_size: Optional[int] = None
    tourney_level: Optional[str] = None
    tourney_date: Optional[int] = None
    
    # Player Seeds/Entries
    winner_seed: Optional[str] = None
    winner_entry: Optional[str] = None
    loser_seed: Optional[str] = None
    loser_entry: Optional[str] = None

    # Match Results
    score: Optional[str] = None
    best_of: Optional[int] = None
    round: Optional[str] = None
    minutes: Optional[float] = None

    # Winner Stats
    w_ace: Optional[int] = None
    w_df: Optional[int] = None
    w_svpt: Optional[int] = None
    w_1stIn: Optional[int] = None
    w_1stWon: Optional[int] = None
    w_2ndWon: Optional[int] = None
    w_SvGms: Optional[int] = None
    w_bpSaved: Optional[int] = None
    w_bpFaced: Optional[int] = None

    # Loser Stats
    l_ace: Optional[int] = None
    l_df: Optional[int] = None
    l_svpt: Optional[int] = None
    l_1stIn: Optional[int] = None
    l_1stWon: Optional[int] = None
    l_2ndWon: Optional[int] = None
    l_SvGms: Optional[int] = None
    l_bpSaved: Optional[int] = None
    l_bpFaced: Optional[int] = None

    # Rankings
    winner_rank: Optional[int] = None
    winner_rank_points: Optional[int] = None
    loser_rank: Optional[int] = None
    loser_rank_points: Optional[int] = None

class MatchCreate(MatchBase):
    winner_id: int
    loser_id: int

class MatchUpdate(MatchBase):
    # Inheriting from MatchBase makes all fields available for update.
    # We set these to None by default so PATCH works correctly.
    tourney_id: Optional[str] = None
    match_num: Optional[int] = None
    winner_id: Optional[int] = None
    loser_id: Optional[int] = None

class Match(MatchBase):
    winner_id: int
    loser_id: int
    
    # Nested Player objects (from our normalization step)
    winner: Optional[Player] = None
    loser: Optional[Player] = None

    class Config:
        from_attributes = True

# --- COMPLEX RESPONSE SCHEMAS ---
class DeleteResponse(BaseModel):
    message: str
    player_id: int

# Use this for a "Player Profile" that includes their rankings
class PlayerDetail(Player):
    rankings: List[Ranking] = []
    
    class Config:
        from_attributes = True

class PlayerSurfaceStat(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    surface: str
    wins: int
    total_matches: int
    win_rate: float

    class Config:
        from_attributes = True

class SurfaceType(str, Enum):
    clay = "Clay"
    grass = "Grass"
    hard = "Hard"

class H2HStat(BaseModel):
    p1_id: int
    p2_id: int
    p1_wins: int
    p2_wins: int
    total_matches: int
    # We reuse your existing Match schema so the user sees the full match details!
    matches: List[Match] 
    
    class Config:
        from_attributes = True

class ServiceKing(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    avg_aces: float
    match_count: int

    class Config:
        from_attributes = True

class GiantSlayer(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    upset_count: int

    class Config:
        from_attributes = True
        
class HallOfFamer(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    weeks_at_no1: int

    class Config:
        from_attributes = True
