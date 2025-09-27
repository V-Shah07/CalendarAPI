import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def add_event(service, title, start_datetime, end_datetime, description="", calendar_id='primary'):
    """
    Add an event to Google Calendar
    
    Args:
        service: Google Calendar service object
        title: Event title (string)
        start_datetime: Start time in format '2024-01-15T09:00:00' 
        end_datetime: End time in format '2024-01-15T11:00:00'
        description: Event description (optional)
    
    Returns:
        Dictionary with event details or error info
    """
    try:
        # Create the event object
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/New_York',  # Change this to your timezone
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/New_York',
            },
        }
        
        # Insert the event
        result = service.events().insert(calendarId= calendar_id, body=event).execute()
        
        return {
            'success': True,
            'event_id': result.get('id'),
            'event_link': result.get('htmlLink'),
            'calendar_id': calendar_id,
            'message': f'Event "{title}" created successfully'
        }
        
    except HttpError as error:
        return {
            'success': False,
            'error': str(error),
            'message': 'Failed to create event'
        }
