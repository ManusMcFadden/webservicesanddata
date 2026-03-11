import pandas as pd
import sqlite3
import os

def create_strictly_filtered_database():
    DB_NAME = "tennis.db"
    
    # --- STEP 1: Identify "Active" IDs from Match Files ---
    # These IDs define who we care about in the entire system
    match_files = [
        'atp_matches_2020.csv', 'atp_matches_2021.csv', 
        'atp_matches_2022.csv', 'atp_matches_2023.csv', 'atp_matches_2024.csv'
    ]
    
    all_matches_list = []
    active_match_ids = set()
    
    print("Step 1: Reading match files to identify active players...")
    for f in match_files:
        if os.path.exists(f):
            df = pd.read_csv(f)
            # Add both winners and losers to our set of active IDs
            active_match_ids.update(df['winner_id'].unique())
            active_match_ids.update(df['loser_id'].unique())
            all_matches_list.append(df)
            print(f"  Processed {f}")

    combined_matches = pd.concat(all_matches_list, ignore_index=True)
    
    # --- STEP 2: Filter Players based on Match IDs ---
    print(f"Step 2: Filtering players list (keeping only {len(active_match_ids)} players seen in matches)...")
    players_df = pd.read_csv('atp_players.csv')
    filtered_players = players_df[players_df['player_id'].isin(active_match_ids)]
    
    # --- STEP 3: Filter Rankings based on Match IDs ---
    print("Step 3: Processing rankings (removing ranks for players without matches)...")
    rank_files = ['atp_rankings_20s.csv', 'atp_rankings_current.csv']
    all_rankings_list = []
    
    for f in rank_files:
        if os.path.exists(f):
            df = pd.read_csv(f)
            # Filter rankings immediately to keep the database lean
            df_filtered = df[df['player'].isin(active_match_ids)]
            all_rankings_list.append(df_filtered)
            print(f"  Processed and filtered {f}")
            
    combined_rankings = pd.DataFrame()
    if all_rankings_list:
        combined_rankings = pd.concat(all_rankings_list, ignore_index=True).drop_duplicates()

    # --- STEP 4: Save to SQLite ---
    conn = sqlite3.connect(DB_NAME)
    print("\nStep 4: Writing to database...")
    
    filtered_players.to_sql('players', conn, if_exists='replace', index=False)

    # Columns that are already in the 'players' table
    redundant_columns = [
        'winner_name', 'winner_hand', 'winner_ht', 'winner_ioc',
        'loser_name', 'loser_hand', 'loser_ht', 'loser_ioc'
    ]
    
    print("Normalizing match data (removing redundant player info)...")
    # Drop these columns from the combined matches DataFrame
    combined_matches = combined_matches.drop(columns=redundant_columns, errors='ignore')

    # Now write to the database
    combined_matches.to_sql('matches', conn, if_exists='replace', index=False)
    
    if not combined_rankings.empty:
        combined_rankings.to_sql('rankings', conn, if_exists='replace', index=False)
        
    print(f"\n✅ Strictly Filtered Database Created!")
    print(f"Total Players in DB:  {len(filtered_players)}")
    print(f"Total Matches in DB:  {len(combined_matches)}")
    print(f"Total Rankings in DB: {len(combined_rankings)}")
    
    conn.close()

if __name__ == "__main__":
    create_strictly_filtered_database()