import sqlite3
from sqlite3 import Error
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AthleteToken:
    athlete_id: int
    access_token: str 
    expires_at: datetime


def create_connection(db_file):
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    
    return conn


def get_athlete_token(conn, athlete_id) -> AthleteToken:
    """Fetch the athlete token object from the athlete_tokens table for a given athlete ID"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT athlete_id, access_token, expires_at
            FROM athlete_tokens 
            WHERE athlete_id = ?
            LIMIT 1
        """, (athlete_id,))
        result = cursor.fetchone()
        
        if result:
            expires_at = datetime.fromtimestamp(result[2], tz=timezone.utc)
            return AthleteToken(
                athlete_id=result[0],
                access_token=result[1],
                expires_at=expires_at
            )
        return None
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        cursor.close()


def upsert_athlete_token(conn, token: AthleteToken) -> bool:
    """Insert or update an athlete's access token record"""
    cursor = conn.cursor()
    
    try:
        utc_timestamp = token.expires_at.astimezone(timezone.utc).timestamp()
        cursor.execute("""
            INSERT INTO athlete_tokens (athlete_id, access_token, expires_at)
            VALUES (?, ?, ?)
            ON CONFLICT(athlete_id) 
            DO UPDATE SET 
                access_token = excluded.access_token,
                expires_at = excluded.expires_at
        """, (token.athlete_id, token.access_token, utc_timestamp))
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
        
    finally:
        cursor.close()


def get_latest_refresh_token(conn, athlete_id):
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT refresh_token 
            FROM athlete_refresh_tokens 
            WHERE athlete_id = ?
            LIMIT 1
        """, (athlete_id,))
        result = cursor.fetchone()
        return result[0] if result else None
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        cursor.close()


def update_refresh_token(conn, athlete_id, refresh_token):
    """Update the refresh token for a given athlete ID"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO athlete_refresh_tokens (athlete_id, refresh_token)
            VALUES (?, ?)
            ON CONFLICT(athlete_id) 
            DO UPDATE SET refresh_token = excluded.refresh_token
        """, (athlete_id, refresh_token))
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
        
    finally:
        cursor.close()


def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS athlete_tokens (
            athlete_id INTEGER PRIMARY KEY,
            access_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL)
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS athlete_refresh_tokens (
            athlete_id INTEGER PRIMARY KEY,
            refresh_token TEXT NOT NULL)
        ''')
        
        conn.commit()
        print("Tables created successfully")
        
    except Error as e:
        print(f"Error creating tables: {e}")


if __name__ == '__main__':
    database = "tokens.db"
    conn = create_connection(database)
    
    if conn is not None:
        print(f"Connected to SQLite version: {sqlite3.version}")
        create_tables(conn)
        conn.close()
    else:
        print("Error: Could not establish database connection")
