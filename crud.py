from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import func, case, Float, or_, and_

# Fetch a single player by ID
def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.player_id == player_id).first()

# Fetch many players with optional filters
def get_players(db: Session, skip: int = 0, limit: int = 100, ioc: str = None):
    query = db.query(models.Player)
    if ioc:
        query = query.filter(models.Player.ioc == ioc.upper())
    return query.offset(skip).limit(limit).all()

# CREATE
def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

# UPDATE
def update_player(db: Session, player_id: int, player_update: schemas.PlayerUpdate):
    db_player = db.query(models.Player).filter(models.Player.player_id == player_id).first()
    if db_player:
        # Update only the fields provided (exclude_unset=True)
        update_data = player_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_player, key, value)
        db.commit()
        db.refresh(db_player)
    return db_player

# DELETE
def delete_player(db: Session, player_id: int):
    db_player = db.query(models.Player).filter(models.Player.player_id == player_id).first()
    if db_player:
        db.delete(db_player)
        db.commit()
        return True
    return False

# Helper to fetch player by name
def get_player_by_name(db: Session, name_first: str, name_last: str):
    return db.query(models.Player).filter(
        func.lower(models.Player.name_first) == name_first.lower(),
        func.lower(models.Player.name_last) == name_last.lower()
    ).first()

# --- MATCH CRUD ---
def get_match(db: Session, tourney_id: str, match_num: int):
    return db.query(models.Match).filter(
        models.Match.tourney_id == tourney_id, 
        models.Match.match_num == match_num
    ).first()

def get_matches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Match).offset(skip).limit(limit).all()

def create_match(db: Session, match: schemas.MatchCreate):
    db_match = models.Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def delete_match(db: Session, tourney_id: str, match_num: int):
    db_match = get_match(db, tourney_id, match_num)
    if db_match:
        db.delete(db_match)
        db.commit()
        return True
    return False

# --- RANKING CRUD ---

def create_ranking(db: Session, ranking: schemas.RankingCreate):
    db_ranking = models.Ranking(**ranking.dict())
    db.add(db_ranking)
    db.commit()
    db.refresh(db_ranking)
    return db_ranking

def delete_ranking(db: Session, ranking_date: int, player_id: int):
    db_rank = get_ranking(db, ranking_date, player_id)
    if db_rank:
        db.delete(db_rank)
        db.commit()
        return True
    return False

def get_rankings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ranking).offset(skip).limit(limit).all()

def get_ranking(db: Session, ranking_date: int, player_id: int):
    return db.query(models.Ranking).filter(
        models.Ranking.ranking_date == ranking_date,
        models.Ranking.player == player_id
    ).first()

def update_ranking(db: Session, ranking_date: int, player_id: int, rank_update: schemas.RankingUpdate):
    db_rank = get_ranking(db, ranking_date, player_id)
    if db_rank:
        # Update only provided fields
        update_data = rank_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_rank, key, value)
        db.commit()
        db.refresh(db_rank)
    return db_rank

# -- ADVANCED OPERATIONS ---

# Fetch rankings for a specific player
def get_player_rankings(db: Session, player_id: int):
    return db.query(models.Ranking).filter(models.Ranking.player == player_id).all()

# Fetch matches for a specific player (where they were winner OR loser)
def get_player_matches(db: Session, player_id: int):
    return db.query(models.Match).filter(
        (models.Match.winner_id == player_id) | (models.Match.loser_id == player_id)
    ).all()

def get_top_players_by_surface(db: Session, surface: str = "Clay", limit: int = 10):
    # 1. Subquery to count wins per player on this surface
    wins_subquery = db.query(
    models.Match.winner_id.label("p_id"),
    func.count(models.Match.match_num).label("win_count")
    ).filter(models.Match.surface == surface).group_by(models.Match.winner_id).subquery()

    # 2. Subquery to count losses per player on this surface
    losses_subquery = db.query(
        models.Match.loser_id.label("p_id"),
        func.count(models.Match.match_num).label("loss_count")
    ).filter(models.Match.surface == surface).group_by(models.Match.loser_id).subquery()

    # 3. Main query
    # We calculate (wins / total_matches) using SQLAlchemy types
    win_rate_expr = (
        func.cast(func.coalesce(wins_subquery.c.win_count, 0), Float) / 
        (func.coalesce(wins_subquery.c.win_count, 0) + func.coalesce(losses_subquery.c.loss_count, 0))
    )

    results = db.query(
        models.Player.player_id,
        models.Player.name_first,
        models.Player.name_last,
        func.coalesce(wins_subquery.c.win_count, 0).label("wins"),
        (func.coalesce(wins_subquery.c.win_count, 0) + func.coalesce(losses_subquery.c.loss_count, 0)).label("total")
    ).outerjoin(wins_subquery, models.Player.player_id == wins_subquery.c.p_id)\
     .outerjoin(losses_subquery, models.Player.player_id == losses_subquery.c.p_id)\
     .filter((func.coalesce(wins_subquery.c.win_count, 0) + func.coalesce(losses_subquery.c.loss_count, 0)) > 5)\
     .order_by(win_rate_expr.desc())\
     .limit(limit).all()

    # 4. Map to list of objects for Pydantic
    return [
        {
            "player_id": r[0], "name_first": r[1], "name_last": r[2],
            "surface": surface, "wins": r[3], "total_matches": r[4],
            "win_rate": round(r[3] / r[4], 3) if r[4] > 0 else 0
        } for r in results
    ]

def get_h2h_matches(db: Session, p1_id: int, p2_id: int):
    # Retrieve all matches where P1 beat P2, OR P2 beat P1
    matches = db.query(models.Match).filter(
        or_(
            and_(models.Match.winner_id == p1_id, models.Match.loser_id == p2_id),
            and_(models.Match.winner_id == p2_id, models.Match.loser_id == p1_id)
        )
    ).order_by(models.Match.tourney_date.desc()).all()

    # Tally up the wins
    p1_wins = sum(1 for match in matches if match.winner_id == p1_id)
    p2_wins = sum(1 for match in matches if match.winner_id == p2_id)

    # Return a dictionary that matches our H2HStat Pydantic schema
    return {
        "p1_id": p1_id,
        "p2_id": p2_id,
        "p1_wins": p1_wins,
        "p2_wins": p2_wins,
        "total_matches": len(matches),
        "matches": matches
    }

def get_service_kings(db: Session, limit: int = 10):
    """
    Calculates the top players based on average aces in winning matches.
    Filters out players with fewer than 10 wins to ensure statistical significance.
    """
    return db.query(
        models.Player.player_id,
        models.Player.name_first,
        models.Player.name_last,
        func.avg(models.Match.w_ace).label("avg_aces"),
        func.count(models.Match.match_num).label("match_count")
    ).join(models.Match, models.Player.player_id == models.Match.winner_id) \
     .group_by(models.Player.player_id) \
     .having(func.count(models.Match.match_num) >= 10) \
     .order_by(func.avg(models.Match.w_ace).desc()) \
     .limit(limit).all()

def get_top_giant_slayers(db: Session, min_rank_gap: int = 50, limit: int = 10):
    """
    Finds players who have defeated opponents ranked much higher than themselves.
    Logic: (loser_rank - winner_rank) > min_rank_gap
    Note: In tennis, a higher rank number (100) is 'lower' than rank 1.
    """
    return db.query(
        models.Player.player_id,
        models.Player.name_first,
        models.Player.name_last,
        func.count(models.Match.match_num).label("upset_count")
    ).join(models.Match, models.Player.player_id == models.Match.winner_id) \
     .filter(models.Match.loser_rank - models.Match.winner_rank >= min_rank_gap) \
     .group_by(models.Player.player_id) \
     .order_by(func.count(models.Match.match_num).desc()) \
     .limit(limit).all()

def get_hall_of_fame(db: Session, limit: int = 10):
    """
    Calculates the all-time leaders for weeks spent at World No. 1.
    Logic: Count all entries in the ranking table where rank == 1.
    """
    return db.query(
        models.Player.player_id,
        models.Player.name_first,
        models.Player.name_last,
        func.count(models.Ranking.ranking_date).label("weeks_at_no1")
    ).join(models.Ranking, models.Player.player_id == models.Ranking.player) \
     .filter(models.Ranking.rank == 1) \
     .group_by(models.Player.player_id) \
     .order_by(func.count(models.Ranking.ranking_date).desc()) \
     .limit(limit).all()

