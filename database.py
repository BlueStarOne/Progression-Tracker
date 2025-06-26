import sqlite3
import datetime

DB_NAME = "user_data.db"
allowed_columns = {"discord_id", "level", "level_exp", "exp", "total_progression", "total_time_driven", "total_distance_driven", "average_speed" }  # Adjust to your actual schema


def insert_or_update_user(discord_id: int, data: dict):
    now = datetime.datetime.now(datetime.UTC).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()

    if row:
        # Fetch column names from the cursor description
        col_names = [desc[0] for desc in cursor.description]
        current_data = dict(zip(col_names, row))

        # Keep only values that are not blank or None
        clean_data = {
            key: value for key, value in data.items()
            if value not in ("", None)
        }

        # Only update if there's something to update
        if clean_data:
            clean_data["row_updated"] = now
            columns = ", ".join([f"{key}=?" for key in clean_data])
            values = list(clean_data.values()) + [discord_id]
            cursor.execute(f"UPDATE users SET {columns} WHERE discord_id = ?", values)
    else:
        # For inserts, allow everything (even blank if explicitly provided)
        data["row_created"] = now
        data["row_updated"] = now
        data["discord_id"] = discord_id
        data["total_progression"] = 0
        data["new_progression"] = 0
        data["races_total"] = 0
        data["races_win"] = 0
        data["races_win_percentage"] = 0
        data["tournaments_total"] = 0
        data["tournaments_win"] = 0
        data["tournaments_win_percentage"] = 0
        data["total_distance_driven"] = 0
        data["total_time_driven"] = 0
        data["average_speed"] = 0
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        cursor.execute(f"INSERT INTO users ({keys}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()


def delete_user(discord_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
    conn.commit()
    conn.close()

def fetch_column_values(column: str):
  """Fetch all values in a specific column across all user rows, along with the total row count."""
  # Sanitize column input
  if column not in allowed_columns:
    raise ValueError(f"Invalid column name: {column}")

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute(f"SELECT {column} FROM users")
  values = [row[0] for row in cursor.fetchall()]
  row_count = len(values)

  conn.close()

  return values, row_count

def fetch_value_by_column(lookup_column: str, lookup_value, target_column: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = f"SELECT {target_column} FROM users WHERE {lookup_column} = ?"
    cursor.execute(query, (lookup_value,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        return None

# delete_user("VectorBlue")
# insert_or_update_user(1006897949822959696,{"discord_id":"1006897949822959696","bbr2_username":"VectorBlue", "total_progression":75,"level":16,"level_exp":1757257,"exp":13900000,"average_speed":184.5,"total_distance_driven":50,"total_time_driven":2})