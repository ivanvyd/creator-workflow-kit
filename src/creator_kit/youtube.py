"""OAuth and reporting limited to explicit read-only YouTube access."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
ANALYTICS_READONLY_SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"
READONLY_SCOPES = {YOUTUBE_READONLY_SCOPE, ANALYTICS_READONLY_SCOPE}


def _stored_scopes(token_file: Path) -> set[str]:
    raw = json.loads(token_file.read_text(encoding="utf-8"))
    scopes = raw.get("scopes", raw.get("scope", []))
    if isinstance(scopes, str):
        scopes = scopes.split()
    if not isinstance(scopes, list) or not all(isinstance(scope, str) for scope in scopes):
        raise PermissionError("token has no readable granted scope list")
    return set(scopes)


def authorize_readonly(credentials_file: Path, token_file: Path) -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow

    if token_file.exists():
        raise FileExistsError("refusing to replace an existing token; choose a new read-only token path")
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), sorted(READONLY_SCOPES))
    credentials = flow.run_local_server(port=0)
    granted = set(credentials.granted_scopes or credentials.scopes or [])
    if not granted or not granted <= READONLY_SCOPES:
        raise PermissionError("OAuth granted scopes include an unsupported permission")
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(credentials.to_json(), encoding="utf-8")


def channel_report(token_file: Path) -> dict[str, object]:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    actual_scopes = _stored_scopes(token_file)
    if not actual_scopes or not actual_scopes <= READONLY_SCOPES or YOUTUBE_READONLY_SCOPE not in actual_scopes:
        raise PermissionError("stored token is not a dedicated allowed read-only token")
    credentials = Credentials.from_authorized_user_file(str(token_file))
    service = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    analytics = build("youtubeAnalytics", "v2", credentials=credentials, cache_discovery=False)
    channel = service.channels().list(part="snippet,statistics", mine=True).execute()
    end_date = datetime.now(UTC).date() - timedelta(days=1)
    start_date = end_date - timedelta(days=27)
    summary = analytics.reports().query(ids="channel==MINE", startDate=start_date.isoformat(), endDate=end_date.isoformat(), metrics="views,estimatedMinutesWatched", dimensions="insightTrafficSourceType").execute()
    return {"channel": channel, "traffic_summary": summary, "scope_check": "stored token contained only approved read-only scopes"}


def write_report(job: Path, report: dict[str, object]) -> Path:
    output = job / "youtube-readonly-report.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return output
