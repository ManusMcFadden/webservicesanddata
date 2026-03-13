from typing import Optional
from mcp.server.fastmcp import FastMCP
from database import SessionLocal
import crud

# Initialize FastMCP
mcp = FastMCP("ATP-Tennis-Manager")

@mcp.tool()
def list_players(skip: int = 0, limit: int = 100, ioc: Optional[str] = None) -> str:
    """Retrieve a list of players with optional pagination and filtering by IOC country code."""
    db = SessionLocal()
    try:
        players = crud.get_players(db, skip=skip, limit=limit, ioc=ioc)
        if not players:
            return "No players found."
        return "\n".join([f"ID: {p.player_id} | {p.name_first} {p.name_last} ({p.ioc})" for p in players])
    finally:
        db.close()

@mcp.tool()
def get_player_profile(player_id: int) -> str:
    """Retrieve detailed metadata for a specific player (DOB, Country, Handedness)."""
    db = SessionLocal()
    try:
        player = crud.get_player(db, player_id=player_id)
        if not player:
            return f"Player with ID {player_id} not found."
        return (f"Name: {player.name_first} {player.name_last}\n"
                f"Country: {player.ioc}\n"
                f"Hand: {player.hand}\n"
                f"Birthdate: {player.dob}")
    finally:
        db.close()

@mcp.tool()
def update_player(player_id: int, name_first: Optional[str] = None, name_last: Optional[str] = None, hand: Optional[str] = None) -> str:
    """Update an existing player's information."""
    db = SessionLocal()
    try:
        player_update = {}
        if name_first:
            player_update["first_name"] = name_first
        if name_last:
            player_update["last_name"] = name_last
        if hand:
            player_update["hand"] = hand
        
        updated_player = crud.update_player(db, player_id=player_id, player_update=player_update)
        if not updated_player:
            return f"Player with ID {player_id} not found."
        return f"Player {updated_player.name_first} {updated_player.name_last} updated successfully."
    finally:
        db.close()

@mcp.tool()
def delete_player(player_id: int) -> str:
    """Delete a player by their unique ID."""
    db = SessionLocal()
    try:
        success = crud.delete_player(db, player_id=player_id)
        if not success:
            return f"Player with ID {player_id} not found."
        return f"Player {player_id} deleted successfully."
    finally:
        db.close()

@mcp.tool()
def create_player(name_first: str, name_last: str, hand: str, ioc: str, dob: str) -> str:
    """Create a new player with the provided information."""
    db = SessionLocal()
    try:
        from datetime import datetime
        player_data = {
            "first_name": name_first,
            "last_name": name_last,
            "hand": hand,
            "ioc": ioc,
            "dob": dob
        }
        db_player = crud.create_player(db=db, player=player_data)
        if db_player is None:
            return "Failed to create player. Please check the input data."
        return f"Player {db_player.name_first} {db_player.name_last} created successfully with ID {db_player.player_id}."
    finally:
        db.close()

@mcp.tool()
def search_player_by_name(name_first: str, name_last: str) -> str:
    """Retrieve a player by their first and last name."""
    db = SessionLocal()
    try:
        player = crud.get_player_by_name(db, name_first=name_first, name_last=name_last)
        if not player:
            return f"No player found with name {name_first} {name_last}."
        return (f"ID: {player.player_id}\n"
                f"Name: {player.name_first} {player.name_last}\n"
                f"Country: {player.ioc}\n"
                f"Hand: {player.hand}\n"
                f"Birthdate: {player.dob}")
    finally:
        db.close()

@mcp.tool()
def get_player_matches(player_id: int) -> str:
    """Retrieve all matches involving a specific player, either as winner or loser."""
    db = SessionLocal()
    try:
        matches = crud.get_player_matches(db, player_id=player_id)
        if not matches:
            return f"No matches found for player {player_id}."
        
        output = []
        for m in matches:
            res = "WON" if m.winner_id == player_id else "LOST"
            opponent_id = m.loser_id if res == "WON" else m.winner_id
            output.append(f"[{m.tourney_date}] {res} vs ID:{opponent_id} | Score: {m.score}")
        return "\n".join(output)
    finally:
        db.close()

@mcp.tool()
def get_player_rankings(player_id: int) -> str:
    """Retrieve all rankings for a specific player."""
    db = SessionLocal()
    try:
        rankings = crud.get_player_rankings(db, player_id=player_id)
        if not rankings:
            return f"No rankings found for player {player_id}."
        return "\n".join([f"Date: {r.ranking_date} | Rank: {r.rank} | Points: {r.points}" for r in rankings])
    finally:
        db.close()

@mcp.tool()
def get_top_players_by_surface(surface: str = "clay", limit: int = 10) -> str:
    """Returns the top players ranked by win rate on a specific surface."""
    db = SessionLocal()
    try:
        players = crud.get_top_players_by_surface(db, surface=surface, limit=limit)
        if not players:
            return f"No players found for surface '{surface}'."
        output = []
        for p in players:
            output.append(f"ID: {p.player_id} | {p.name_first} {p.name_last}")
        return "\n".join(output)
    finally:
        db.close()

@mcp.tool()
def get_service_kings(limit: int = 10) -> str:
    """Get a leaderboard of the best servers (highest average aces per win). Only includes players with at least 10 recorded wins."""
    db = SessionLocal()
    try:
        stats = crud.get_service_kings(db, limit=limit)
        if not stats:
            return "No service statistics found."
        output = []
        for stat in stats:
            output.append(f"Player ID: {stat.player_id} | Avg Aces: {stat.avg_aces:.2f}")
        return "\n".join(output)
    finally:
        db.close()

@mcp.tool()
def get_giant_slayers(min_gap: int = 50, limit: int = 10) -> str:
    """Returns a leaderboard of players with the most 'upset' wins. An upset is defined by the gap between winner and loser rank."""
    db = SessionLocal()
    try:
        slayers = crud.get_top_giant_slayers(db, min_rank_gap=min_gap, limit=limit)
        if not slayers:
            return f"No giant slayers found with minimum rank gap of {min_gap}."
        output = []
        for slayer in slayers:
            output.append(f"Player ID: {slayer.player_id} | Upset Wins: {slayer.upset_count}")
        return "\n".join(output)
    finally:
        db.close()

@mcp.tool()
def list_matches(skip: int = 0, limit: int = 100) -> str:
    """Retrieve a list of matches with pagination."""
    db = SessionLocal()
    try:
        matches = crud.get_matches(db, skip=skip, limit=limit)
        if not matches:
            return "No matches found."
        output = []
        for m in matches:
            output.append(f"Tournament: {m.tourney_id} | Match: {m.match_num} | Winner ID: {m.winner_id} | Loser ID: {m.loser_id} | Score: {m.score}")
        return "\n".join(output)
    finally:
        db.close()

@mcp.tool()
def get_match(tourney_id: str, match_num: int) -> str:
    """Retrieve a specific match using its tournament ID and match number."""
    db = SessionLocal()
    try:
        match = crud.get_match(db, tourney_id=tourney_id, match_num=match_num)
        if not match:
            return f"Match not found for tournament {tourney_id} and match number {match_num}."
        return (f"Tournament: {match.tourney_id}\n"
                f"Match Number: {match.match_num}\n"
                f"Winner ID: {match.winner_id}\n"
                f"Loser ID: {match.loser_id}\n"
                f"Score: {match.score}\n"
                f"Date: {match.tourney_date}")
    finally:
        db.close()

@mcp.tool()
def create_match(tourney_id: str, match_num: int, winner_id: int, loser_id: int, score: str, tourney_date: str) -> str:
    """Add a new match to the database."""
    db = SessionLocal()
    try:
        match_data = {
            "tourney_id": tourney_id,
            "match_num": match_num,
            "winner_id": winner_id,
            "loser_id": loser_id,
            "score": score,
            "tourney_date": tourney_date
        }
        db_match = crud.create_match(db=db, match=match_data)
        if db_match is None:
            return "Failed to create match. Please check the input data."
        return f"Match created successfully for tournament {db_match.tourney_id}."
    finally:
        db.close()

@mcp.tool()
def update_match(tourney_id: str, match_num: int, score: Optional[str] = None, tourney_date: Optional[str] = None) -> str:
    """Update specific fields of an existing match (e.g., score or date)."""
    db = SessionLocal()
    try:
        match_update = {}
        if score:
            match_update["score"] = score
        if tourney_date:
            match_update["tourney_date"] = tourney_date
        
        updated_match = crud.update_match(db, tourney_id=tourney_id, match_num=match_num, match_update=match_update)
        if not updated_match:
            return f"Match not found for tournament {tourney_id} and match number {match_num}."
        return f"Match updated successfully."
    finally:
        db.close()

@mcp.tool()
def delete_match(tourney_id: str, match_num: int) -> str:
    """Remove a match from the database."""
    db = SessionLocal()
    try:
        success = crud.delete_match(db, tourney_id, match_num)
        if not success:
            return f"Match not found for tournament {tourney_id} and match number {match_num}."
        return f"Match deleted successfully."
    finally:
        db.close()

@mcp.tool()
def get_head_to_head(p1_id: int, p2_id: int) -> str:
    """Retrieve the head-to-head match history and win statistics between two specific players."""
    db = SessionLocal()
    try:
        player1 = crud.get_player(db, player_id=p1_id)
        player2 = crud.get_player(db, player_id=p2_id)
        
        if not player1 or not player2:
            return "One or both players not found in the database."
        
        h2h_data = crud.get_h2h_matches(db, p1_id=p1_id, p2_id=p2_id)
        
        if h2h_data["total_matches"] == 0:
            return f"Players {p1_id} and {p2_id} have never played against each other."
        
        return (f"Head-to-Head: Player {p1_id} vs Player {p2_id}\n"
                f"Total Matches: {h2h_data['total_matches']}\n"
                f"Player {p1_id} Wins: {h2h_data['p1_wins']}\n"
                f"Player {p2_id} Wins: {h2h_data['p2_wins']}")
    finally:
        db.close()

@mcp.tool()
def list_rankings(skip: int = 0, limit: int = 100) -> str:
    """Retrieve a list of rankings with pagination."""
    db = SessionLocal()
    try:
        rankings = crud.get_rankings(db, skip=skip, limit=limit)
        if not rankings:
            return "No rankings found."
        return "\n".join([f"Date: {r.ranking_date} | Player ID: {r.player_id} | Rank: {r.rank} | Points: {r.points}" for r in rankings])
    finally:
        db.close()

@mcp.tool()
def get_ranking(ranking_date: int, player_id: int) -> str:
    """Retrieve a specific ranking entry by date and player ID."""
    db = SessionLocal()
    try:
        ranking = crud.get_ranking(db, ranking_date=ranking_date, player_id=player_id)
        if not ranking:
            return f"Ranking entry not found for date {ranking_date} and player {player_id}."
        return (f"Date: {ranking.ranking_date}\n"
                f"Player ID: {ranking.player_id}\n"
                f"Rank: {ranking.rank}\n"
                f"Points: {ranking.points}")
    finally:
        db.close()

@mcp.tool()
def create_ranking(ranking_date: int, player_id: int, rank: int, points: int) -> str:
    """Create a new ranking entry for a player on a specific date."""
    db = SessionLocal()
    try:
        ranking_data = {
            "ranking_date": ranking_date,
            "player_id": player_id,
            "rank": rank,
            "points": points
        }
        db_ranking = crud.create_ranking(db=db, ranking=ranking_data)
        if db_ranking is None:
            return "Failed to create ranking. Please check the input data."
        return f"Ranking created successfully for player {player_id} on date {ranking_date}."
    finally:
        db.close()

@mcp.tool()
def update_ranking(ranking_date: int, player_id: int, rank: Optional[int] = None, points: Optional[int] = None) -> str:
    """Update a specific ranking entry (e.g., change rank or points)."""
    db = SessionLocal()
    try:
        rank_update = {}
        if rank is not None:
            rank_update["rank"] = rank
        if points is not None:
            rank_update["points"] = points
        
        updated_ranking = crud.update_ranking(db, ranking_date=ranking_date, player_id=player_id, rank_update=rank_update)
        if not updated_ranking:
            return f"Ranking entry not found for date {ranking_date} and player {player_id}."
        return f"Ranking updated successfully."
    finally:
        db.close()

@mcp.tool()
def delete_ranking(ranking_date: int, player_id: int) -> str:
    """Delete a specific ranking entry by date and player ID."""
    db = SessionLocal()
    try:
        success = crud.delete_ranking(db, ranking_date, player_id)
        if not success:
            return f"Ranking entry not found for date {ranking_date} and player {player_id}."
        return f"Ranking deleted successfully."
    finally:
        db.close()

@mcp.tool()
def get_hall_of_fame(limit: int = 10) -> str:
    """Returns an all-time leaderboard of players who have spent the most weeks ranked as World Number 1."""
    db = SessionLocal()
    try:
        stats = crud.get_hall_of_fame(db, limit=limit)
        if not stats:
            return "No ranking data found."
        output = []
        for stat in stats:
            output.append(f"Player ID: {stat.player_id} | Weeks at #1: {stat.weeks_at_one}")
        return "\n".join(output)
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()