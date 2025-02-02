import os

import httpx

CLIENT_ID=os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET=os.getenv("STRAVA_CLIENT_SECRET")
API_URL="https://www.strava.com/api/v3"
ACTIVITIES_URL="/athlete/activities"
TOKEN_URL="/oauth/token"


async def get_oauth_token(refresh_token: str) -> dict | None:
    """
    Fetch a new OAuth token from Strava using a refresh token.
    Returns the token response as a dictionary containing access_token, refresh_token etc.
    Returns None if the request fails.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}{TOKEN_URL}",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"Error refreshing token: {e}")
        print(f"HTTP Response Body: {e.response.text}")
        return None


async def get_activities(access_token: str) -> list[dict]:
    """
    Fetch activities from Strava using an access token.
    Returns a list of activity dictionaries containing activity details.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}{ACTIVITIES_URL}",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"Error fetching activities: {e}")
        return []
