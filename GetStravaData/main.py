import json
from pathlib import Path
from typing import Any

import httpx

API_URL = "https://www.strava.com/api/v3/athlete/activities"
TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
CREDENTIALS_PATH = Path(".strava_credentials.json")
OUTPUT_PATH = Path("output.json")


def load_credentials() -> dict[str, str]:
    """Load OAuth credentials from the local JSON file."""
    if not CREDENTIALS_PATH.exists():
        raise RuntimeError(
            "Missing .strava_credentials.json. Copy strava_credentials.example.json "
            "and fill in your client_id, client_secret, refresh_token, and access_token."
        )

    creds = json.loads(CREDENTIALS_PATH.read_text())
    required = ("client_id", "client_secret", "refresh_token")
    missing = [field for field in required if not creds.get(field)]
    if missing:
        raise RuntimeError(
            f"Missing required field(s) {', '.join(missing)} in {CREDENTIALS_PATH}."
        )

    return creds


def save_credentials(creds: dict[str, str]) -> None:
    """Persist credential updates (new access/refresh tokens)."""
    CREDENTIALS_PATH.write_text(json.dumps(creds, indent=2))


def refresh_access_token(creds: dict[str, str]) -> dict[str, str]:
    """Refresh the short-lived Strava access token."""
    payload = {
        "client_id": str(creds["client_id"]),
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token",
    }

    with httpx.Client(timeout=httpx.Timeout(10.0, read=30.0)) as client:
        response = client.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        token_payload = response.json()

    creds["access_token"] = token_payload["access_token"]
    # Strava rotates refresh tokens, so persist the new one when it is returned.
    if token_payload.get("refresh_token"):
        creds["refresh_token"] = token_payload["refresh_token"]

    save_credentials(creds)
    return creds


def fetch_activities(access_token: str, per_page: int = 30, max_pages: int = 1) -> list[dict[str, Any]]:
    """Fetch the athlete's recent activities from Strava."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    activities: list[dict[str, Any]] = []

    with httpx.Client(timeout=httpx.Timeout(10.0, read=30.0)) as client:
        for page in range(1, max_pages + 1):
            response = client.get(
                API_URL,
                headers=headers,
                params={"page": page, "per_page": per_page},
            )
            response.raise_for_status()

            batch = response.json()
            if not batch:
                break
            activities.extend(batch)

    return activities


def main() -> None:
    creds = load_credentials()
    access_token = creds.get("access_token") or ""

    if not access_token:
        creds = refresh_access_token(creds)
        access_token = creds["access_token"]

    try:
        activities = fetch_activities(access_token, per_page=50, max_pages=1)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            creds = refresh_access_token(creds)
            activities = fetch_activities(creds["access_token"], per_page=50, max_pages=1)
        else:
            error_body = exc.response.text
            print(f"Strava API error ({exc.response.status_code}): {error_body}")
            raise

    OUTPUT_PATH.write_text(json.dumps(activities, indent=2))
    print(f"Fetched {len(activities)} activities. Saved to {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()
