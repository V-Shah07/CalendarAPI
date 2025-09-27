import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def create_calendar(service, calendar_name, description=""):
    """
    Create a new calendar
    
    Args:
        service: Google Calendar service object
        calendar_name: Name for the new calendar
        description: Description for the calendar (optional)
    
    Returns:
        Dictionary with calendar details or error info
    """
    try:
        calendar = {
            'summary': calendar_name,
            'description': description,
            'timeZone': 'America/New_York'  # Change to your timezone
        }
        
        created_calendar = service.calendars().insert(body=calendar).execute()
        
        return {
            'success': True,
            'calendar_id': created_calendar['id'],
            'calendar_name': created_calendar['summary'],
            'message': f'Calendar "{calendar_name}" created successfully'
        }
        
    except HttpError as error:
        return {
            'success': False,
            'error': str(error),
            'message': 'Failed to create calendar'
        }