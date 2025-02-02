import os
import datetime
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import strava
import database as db

DB_FILE = os.getenv("DB_FILE")
ATHLETE_ID = 3721045

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

async def get_access_token(conn: sqlite3.Connection, athlete_id: int):
    token = db.get_athlete_token(conn, athlete_id)
    if token is None:
        return None
    if token.expires_at > datetime.datetime.now(datetime.UTC):
        return token.access_token
    
    refresh_token = db.get_latest_refresh_token(conn, athlete_id)
    if refresh_token is None:
        return None
    
    token_info = await strava.get_oauth_token(refresh_token)
    if token_info is None:
        return None
    expiry = datetime.datetime.fromtimestamp(token_info["expires_at"], tz=datetime.UTC)
    success = db.upsert_athlete_token(conn, db.AthleteToken(athlete_id, token_info["access_token"], expiry))
    if not success:
        print("failed to upsert token")
    success = db.update_refresh_token(conn, athlete_id, token_info["refresh_token"])
    if not success:
        print("failed to update refresh token")
    print("refreshed token")
    return token_info["access_token"]


@app.get("/workout-dates", response_model=list[str])
async def root():
    conn = db.create_connection(DB_FILE)
    if conn is None:
        return []
    access_token = await get_access_token(conn, ATHLETE_ID)
    if access_token is None:
        return []
    data = await strava.get_activities(access_token)
    dates = []
    for activity in data:
        date_string = activity["start_date_local"]
        dt = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        dates.append(dt.strftime('%Y-%m-%d'))
    
    return dates

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
