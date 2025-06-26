import sqlite3

DB_NAME = "user_data.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        discord_id TEXT PRIMARY KEY,
        bbr2_username TEXT,
        level INTEGER,
        level_exp INTEGER,
        exp INTEGER,
        cars INTEGER,
        cars_skins INTEGER,
        drivers INTEGER,
        drivers_skins INTEGER,
        tracks INTEGER,
        powerups INTEGER,
        common_upgrades INTEGER,
        rare_upgrades INTEGER,
        epic_upgrades INTEGER,
        races_total INTEGER,
        races_win INTEGER,
        races_win_percentage REAL,
        tournaments_total INTEGER,
        tournaments_win INTEGER,
        tournaments_win_percentage REAL,
        total_distance_driven REAL,
        total_time_driven REAL,
        average_speed REAL,
        total_progression REAL,
        new_progression REAL,
        exp_progression REAL,
        cars_progression REAL,
        cars_skins_progression REAL,
        drivers_progression REAL,
        drivers_skins_progression REAL,
        tracks_progression REAL,
        powerups_progression REAL,
        common_progression REAL,
        rare_progression REAL,
        epic_progression REAL,
        row_created TEXT,
        row_updated TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database and table created.")

def delete_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    print("🗑️ All user rows deleted.")

# Example usage:
delete_all_users()
# delete_all_users()  # Uncomment to clear the table
