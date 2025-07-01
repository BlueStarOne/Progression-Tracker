import sqlite3
import csv
import datetime

DB_NAME = "user_data.db"
allowed_columns = {"discord_id", "level", "level_exp", "exp", "total_progression", "total_time_driven", "total_distance_driven", "average_speed", "bbr2_username", "level", "exp", "cars", "cars_skins", "drivers", "drivers_skins",
        "powerups", "common_upgrades", "rare_upgrades", "epic_upgrades", "tracks",
        "races_total", "races_win", "races_win_percentage", "tournaments_total",
        "tournaments_win", "tournaments_win_percentage", "total_time_driven",
        "total_distance_driven", "average_speed", "new_progression" }  # Adjust to your actual schema

def log(text: str, filename: str = "logs.txt") -> None:
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}: {text}\n")

def admin_database_management(discord_id: str, column: str, new_value: str, delete_row: bool) -> bool:
    """
    Allows the bot owner to modify or delete a user's row in the database.

    :param discord_id: The Discord user ID (as a string).
    :param column: The column (field) to update.
    :param new_value: The new value to assign to the column.
    :param delete_row: If True, deletes the user's row instead of updating.
    :return: True if the operation was successful, False otherwise.
    """

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if delete_row:
            cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
            conn.commit()
            return cursor.rowcount > 0

        # Prevent updating unapproved fields
        if column not in allowed_columns:
            db.log(f"Rejected update: Invalid column '{column}'")
            return "Invalid column"

        cursor.execute(f"""
            UPDATE users
            SET {column} = ?
            WHERE discord_id = ?
        """, (new_value, discord_id))
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        db.log(f"Database error in admin_database_management: {e}")
        return False

    finally:
        conn.close()


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

def fetch_value_by_column(lookup_value, lookup_column: str, target_column: str):
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
        
def check_if_exists(column: str, value) -> bool:
    conn = sqlite3.connect(DB_NAME)  # adjust path as needed
    cursor = conn.cursor()

    try:
        query = f"SELECT 1 FROM users WHERE {column} = ? LIMIT 1"
        cursor.execute(query, (value,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        db.log(f"Database error: {e}")
        return False
    finally:
        conn.close()

def fetch_leaderboard(column: str, limit: int = 10, descending: bool = True):
    """
    Fetches the top users sorted by the given column.

    :param column: The column to sort by (e.g. 'exp', 'races_win')
    :param limit: Max number of results to return
    :param descending: Whether to sort descending (True for leaderboard)
    :return: List of tuples with (discord_id, column_value)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    order = "DESC" if descending else "ASC"

    try:
        cursor.execute(f"""
            SELECT discord_id, {column}
            FROM users
            WHERE {column} IS NOT NULL
            ORDER BY {column} {order}
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        db.log(f"Database error: {e}")
        return []
    finally:
        conn.close()


def fetch_leaderboard_by_columns(columns: list[str], limit: int = 10, descending: bool = True):
    """
    Fetches the top users sorted by multiple columns.

    :param columns: List of column names to sort by in priority order (e.g. ['level', 'exp'])
    :param limit: Max number of results to return
    :param descending: Whether to sort descending (applies to all columns)
    :return: List of tuples with (discord_id, column1, column2, ...)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    order = "DESC" if descending else "ASC"
    column_str = ", ".join(columns)
    order_by_str = ", ".join(f"{col} {order}" for col in columns)

    try:
        cursor.execute(f"""
            SELECT discord_id, {column_str}
            FROM users
            WHERE {' AND '.join(f"{col} IS NOT NULL" for col in columns)}
            ORDER BY {order_by_str}
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        db.log(f"Database error: {e}")
        return []
    finally:
        conn.close()

def export_database_to_csv(csv_file_path: str = "exported_data.csv") -> bool:
    """
    Exports the users table to a CSV file.

    :param csv_file_path: Path to save the CSV file
    :return: True if export was successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(rows)

        return True
    except Exception as e:
        db.log(f"Export failed: {e}")
        return False
    finally:
        conn.close()


# delete_user("VectorBlue")
# insert_or_update_user(1006897949822959696,{"discord_id":"1006897949822959696","bbr2_username":"VectorBlue", "total_progression":75,"level":16,"level_exp":1757257,"exp":13900000,"average_speed":184.5,"total_distance_driven":50,"total_time_driven":2})