from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum

# --- ENUMS ---
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "name_first": "Roger",
                "name_last": "Federer",
                "hand": "R",
                "dob": 19810808,
                "ioc": "SUI",
                "height": 185.0
            }
        }
    }

class PlayerCreate(PlayerBase):
    player_id: int 

    model_config = {
        "json_schema_extra": {
            "example": {
                "player_id": 104925,
                "name_first": "Novak",
                "name_last": "Djokovic",
                "hand": "R",
                "dob": 19870522,
                "ioc": "SRB",
                "height": 188.0
            }
        }
    }

class Player(PlayerBase):
    player_id: int
    wikidata_id: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "player_id": 104925,
                "name_first": "Novak",
                "name_last": "Djokovic",
                "hand": "R",
                "dob": 19870522,
                "ioc": "SRB",
                "height": 188.0,
                "wikidata_id": "Q5812"
            }
        }
    )

class PlayerUpdate(BaseModel):
    name_first: Optional[str] = None
    name_last: Optional[str] = None
    hand: Optional[str] = None
    height: Optional[float] = None
    ioc: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name_first": "Roger",
                "name_last": "Federer",
                "hand": "R",
                "height": 185.0,
                "ioc": "SUI"
            }
        }
    }

# --- RANKING SCHEMAS ---
class RankingBase(BaseModel):
    ranking_date: int
    rank: int
    points: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "ranking_date": 20240101,
                "rank": 1,
                "points": 11055
            }
        }
    }

class Ranking(RankingBase):
    player: int
    player_details: Optional[Player] = None 

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "ranking_date": 20240101,
                "rank": 1,
                "points": 11055,
                "player": 104925,
                "player_details": {
                    "player_id": 104925,
                    "name_first": "Novak",
                    "name_last": "Djokovic",
                    "ioc": "SRB"
                }
            }
        }
    )

class RankingCreate(RankingBase):
    player: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "ranking_date": 20240101,
                "rank": 1,
                "points": 11055,
                "player": 104925
            }
        }
    }

class RankingUpdate(BaseModel):
    rank: Optional[int] = None
    points: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "rank": 2,
                "points": 10500
            }
        }
    }

# --- MATCH SCHEMAS ---

class MatchBase(BaseModel):
    tourney_id: str
    match_num: int
    tourney_name: Optional[str] = None
    surface: Optional[str] = None
    draw_size: Optional[int] = None
    tourney_level: Optional[str] = None
    tourney_date: Optional[int] = None
    winner_seed: Optional[str] = None
    winner_entry: Optional[str] = None
    loser_seed: Optional[str] = None
    loser_entry: Optional[str] = None
    score: Optional[str] = None
    best_of: Optional[int] = None
    round: Optional[str] = None
    minutes: Optional[float] = None
    w_ace: Optional[int] = None
    w_df: Optional[int] = None
    w_svpt: Optional[int] = None
    w_1stIn: Optional[int] = None
    w_1stWon: Optional[int] = None
    w_2ndWon: Optional[int] = None
    w_SvGms: Optional[int] = None
    w_bpSaved: Optional[int] = None
    w_bpFaced: Optional[int] = None
    l_ace: Optional[int] = None
    l_df: Optional[int] = None
    l_svpt: Optional[int] = None
    l_1stIn: Optional[int] = None
    l_1stWon: Optional[int] = None
    l_2ndWon: Optional[int] = None
    l_SvGms: Optional[int] = None
    l_bpSaved: Optional[int] = None
    l_bpFaced: Optional[int] = None
    winner_rank: Optional[int] = None
    winner_rank_points: Optional[int] = None
    loser_rank: Optional[int] = None
    loser_rank_points: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "tourney_id": "2023-520",
                "match_num": 1,
                "tourney_name": "Roland Garros",
                "surface": "Clay",
                "score": "6-3 6-2 6-3",
                "round": "F",
                "w_ace": 11,
                "l_ace": 4
            }
        }
    }

class MatchCreate(MatchBase):
    winner_id: int
    loser_id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "tourney_id": "2023-520",
                "match_num": 1,
                "tourney_name": "Roland Garros",
                "surface": "Clay",
                "score": "6-3 6-2 6-3",
                "round": "F",
                "w_ace": 11,
                "l_ace": 4,
                "winner_id": 104925,
                "loser_id": 104745
            }
        }
    }

class MatchUpdate(MatchBase):
    tourney_id: Optional[str] = None
    match_num: Optional[int] = None
    winner_id: Optional[int] = None
    loser_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "tourney_id": "2023-520",
                "match_num": 1,
                "surface": "Clay",
                "score": "6-4 6-3 6-2",
                "round": "F",
                "w_ace": 15,
                "l_ace": 5,
                "winner_id": 104925,
                "loser_id": 104745
            }
        }
    }

class Match(MatchBase):
    winner_id: int
    loser_id: int
    winner: Optional[Player] = None
    loser: Optional[Player] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "tourney_id": "2023-520",
                "match_num": 1,
                "tourney_name": "Roland Garros",
                "surface": "Clay",
                "score": "6-3 6-2 6-3",
                "round": "F",
                "w_ace": 11,
                "l_ace": 4,
                "winner_id": 104925,
                "loser_id": 104745,
                "winner": {
                    "player_id": 104925,
                    "name_first": "Novak",
                    "name_last": "Djokovic",
                    "ioc": "SRB"
                },
                "loser": {
                    "player_id": 104745,
                    "name_first": "Rafael",
                    "name_last": "Nadal",
                    "ioc": "ESP"
                }
            }
        }
    )

# --- COMPLEX RESPONSE SCHEMAS ---
class DeleteResponse(BaseModel):
    message: str
    player_id: int

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Player deleted successfully", "player_id": 104925}
        }
    }

class PlayerDetail(Player):
    rankings: List[Ranking] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "player_id": 104925,
                "name_first": "Novak",
                "name_last": "Djokovic",
                "hand": "R",
                "dob": 19870522,
                "ioc": "SRB",
                "height": 188.0,
                "wikidata_id": "Q5812",
                "rankings": [
                    {
                        "ranking_date": 20240101,
                        "rank": 1,
                        "points": 11055,
                        "player": 104925
                    }
                ]
            }
        }
    )

class PlayerSurfaceStat(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    surface: str
    wins: int
    total_matches: int
    win_rate: float

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "player_id": 104745,
                "name_first": "Rafael",
                "name_last": "Nadal",
                "surface": "Clay",
                "wins": 474,
                "total_matches": 519,
                "win_rate": 0.913
            }
        }
    )

class H2HStat(BaseModel):
    p1_id: int
    p2_id: int
    p1_wins: int
    p2_wins: int
    total_matches: int
    matches: List[Match] 
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "p1_id": 104925,
                "p2_id": 104745,
                "p1_wins": 30,
                "p2_wins": 29,
                "total_matches": 59,
                "matches": []
            }
        }
    )

class ServiceKing(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    avg_aces: float
    match_count: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "player_id": 103852,
                "name_first": "Feliciano",
                "name_last": "Lopez",
                "avg_aces": 14.5,
                "match_count": 450
            }
        }
    )

class GiantSlayer(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    upset_count: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "player_id": 106401,
                "name_first": "Nick",
                "name_last": "Kyrgios",
                "upset_count": 12
            }
        }
    )
        
class HallOfFamer(BaseModel):
    player_id: int
    name_first: str
    name_last: str
    weeks_at_no1: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "player_id": 104925,
                "name_first": "Novak",
                "name_last": "Djokovic",
                "weeks_at_no1": 428
            }
        }
    )