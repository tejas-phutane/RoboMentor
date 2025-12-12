import os
import datetime
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarIntegration:
    """Handles Google Calendar OAuth2 authentication and event management."""

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
              'https://www.googleapis.com/auth/calendar.events']

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API using OAuth2."""
        try:
            self.creds = None
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")

                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)

                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())

            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_events(self, calendar_id: str = 'primary', time_min: Optional[datetime.datetime] = None,
                   time_max: Optional[datetime.datetime] = None, max_results: int = 250) -> List[Dict]:
        """Retrieve events from the specified calendar within the given time range."""
        if not self.service:
            if not self.authenticate():
                return []

        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z' if time_min else None,
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])
        except HttpError as e:
            print(f"Error retrieving events: {e}")
            return []

    def create_event(self, calendar_id: str = 'primary', summary: str = '', description: str = '',
                     start_time: Optional[datetime.datetime] = None, end_time: Optional[datetime.datetime] = None,
                     timezone: str = 'UTC') -> Optional[Dict]:
        """Create a new event in the specified calendar."""
        if not self.service:
            if not self.authenticate():
                return None

        if not start_time or not end_time:
            raise ValueError("Start time and end time are required")

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': timezone,
            },
        }

        try:
            created_event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return created_event
        except HttpError as e:
            print(f"Error creating event: {e}")
            return None

    def update_event(self, calendar_id: str = 'primary', event_id: str = '',
                     updates: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Update an existing event in the specified calendar."""
        if not self.service:
            if not self.authenticate():
                return None

        if not updates:
            return None

        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            event.update(updates)
            updated_event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            return updated_event
        except HttpError as e:
            print(f"Error updating event: {e}")
            return None

    def delete_event(self, calendar_id: str = 'primary', event_id: str = '') -> bool:
        """Delete an event from the specified calendar."""
        if not self.service:
            if not self.authenticate():
                return False

        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return True
        except HttpError as e:
            print(f"Error deleting event: {e}")
            return False

    def get_free_busy(self, calendar_id: str = 'primary', time_min: Optional[datetime.datetime] = None,
                      time_max: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        """Get free/busy information for the specified calendar."""
        if not self.service:
            if not self.authenticate():
                return []

        try:
            body = {
                "timeMin": time_min.isoformat() + 'Z' if time_min else None,
                "timeMax": time_max.isoformat() + 'Z' if time_max else None,
                "items": [{"id": calendar_id}]
            }

            freebusy_result = self.service.freebusy().query(body=body).execute()
            return freebusy_result.get('calendars', {}).get(calendar_id, {}).get('busy', [])
        except HttpError as e:
            print(f"Error retrieving free/busy info: {e}")
            return []