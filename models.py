from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, index=True)
    name_first = Column(String)
    name_last = Column(String)
    hand = Column(String)
    dob = Column(Integer)
    ioc = Column(String)
    height = Column(Float)
    wikidata_id = Column(String)

class Match(Base):
    __tablename__ = "matches"

    # Composite Primary Key
    tourney_id = Column(String, primary_key=True)
    match_num = Column(Integer, primary_key=True)
    
    # Tournament Details
    tourney_name = Column(String)
    surface = Column(String)
    draw_size = Column(Integer)
    tourney_level = Column(String)
    tourney_date = Column(Integer)
    
    # Player Identifiers (Foreign Keys)
    winner_id = Column(Integer, ForeignKey("players.player_id"))
    loser_id = Column(Integer, ForeignKey("players.player_id"))
    
    # Non-redundant Player Info
    winner_seed = Column(String, nullable=True)
    winner_entry = Column(String, nullable=True)
    loser_seed = Column(String, nullable=True)
    loser_entry = Column(String, nullable=True)

    # Match Results
    score = Column(String)
    best_of = Column(Integer)
    round = Column(String)
    minutes = Column(Float, nullable=True)

    # Winner Stats
    w_ace = Column(Integer, nullable=True)
    w_df = Column(Integer, nullable=True)
    w_svpt = Column(Integer, nullable=True)
    w_1stIn = Column(Integer, nullable=True)
    w_1stWon = Column(Integer, nullable=True)
    w_2ndWon = Column(Integer, nullable=True)
    w_SvGms = Column(Integer, nullable=True)
    w_bpSaved = Column(Integer, nullable=True)
    w_bpFaced = Column(Integer, nullable=True)

    # Loser Stats
    l_ace = Column(Integer, nullable=True)
    l_df = Column(Integer, nullable=True)
    l_svpt = Column(Integer, nullable=True)
    l_1stIn = Column(Integer, nullable=True)
    l_1stWon = Column(Integer, nullable=True)
    l_2ndWon = Column(Integer, nullable=True)
    l_SvGms = Column(Integer, nullable=True)
    l_bpSaved = Column(Integer, nullable=True)
    l_bpFaced = Column(Integer, nullable=True)

    # Rankings at time of match
    winner_rank = Column(Integer, nullable=True)
    winner_rank_points = Column(Integer, nullable=True)
    loser_rank = Column(Integer, nullable=True)
    loser_rank_points = Column(Integer, nullable=True)

    # ORM Relationships
    winner = relationship("Player", foreign_keys=[winner_id])
    loser = relationship("Player", foreign_keys=[loser_id])

class Ranking(Base):
    __tablename__ = "rankings"

    ranking_date = Column(Integer, primary_key=True)
    player = Column(Integer, ForeignKey("players.player_id"), primary_key=True)
    rank = Column(Integer)
    points = Column(Integer)

    # Add this relationship
    # This tells SQLAlchemy to fetch the Player object linked to the 'player' ID
    player_details = relationship("Player")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)