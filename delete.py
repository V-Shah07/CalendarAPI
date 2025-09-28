import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def find_event_by_title_and_time(service, title, start_datetime, calendar_id='primary'):
    """
    Find an event by its title and start time
    
    Args:
        service: Google Calendar service object
        title: Event title to search for
        start_datetime: Start time in format '2024-01-15T09:00:00'
        calendar_id: Calendar ID to search in (default: 'primary')
    
    Returns:
        Dictionary with event details or error info
    """
    try:
        # Convert start_datetime to the right format for search
        # We'll search for events on that day
        date_part = start_datetime.split('T')[0]  # Get just the date part
        time_min = date_part + 'T00:00:00-05:00'  # Add timezone
        time_max = date_part + 'T23:59:59-05:00'  # Add timezone
        
        print(f"Searching for events between {time_min} and {time_max}")
        
        # Get events for that day
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"Found {len(events)} events on that day")
        
        # Search for matching title and start time
        for event in events:
            event_title = event.get('summary', '')
            event_start = event['start'].get('dateTime', '')
            
            print(f"Checking event: '{event_title}' at {event_start}")
            
            # Extract just the date and time part (ignore timezone)
            # Format: 2025-12-15T09:00:00-05:00
            if 'T' in event_start:
                # Find the last occurrence of + or - (for timezone)
                if '+' in event_start:
                    event_start_clean = event_start.split('+')[0]
                elif event_start.count('-') > 2:  # More than 2 dashes means timezone
                    # Find last dash that's part of timezone (not date)
                    parts = event_start.split('-')
                    event_start_clean = '-'.join(parts[:-1])  # Everything except last part
                else:
                    event_start_clean = event_start.split('Z')[0]
            else:
                event_start_clean = event_start
            
            print(f"Comparing '{title.lower()}' with '{event_title.lower()}'")
            print(f"Comparing times: '{start_datetime}' with '{event_start_clean}'")
            
            # Check if title matches and start time matches
            if title.lower() == event_title.lower() and start_datetime == event_start_clean:
                print(f"✅ Match found!")
                return {
                    'success': True,
                    'event_id': event.get('id'),
                    'event_title': event.get('summary'),
                    'current_start': event_start,
                    'current_end': event['end'].get('dateTime', ''),
                    'message': f'Found event "{event.get("summary")}"'
                }
        
        print("❌ No matching event found")
        return {
            'success': False,
            'message': f'No event found with title "{title}" at time {start_datetime}'
        }
        
    except HttpError as error:
        return {
            'success': False,
            'error': str(error),
            'message': 'Failed to search for event'
        }


def delete_event_by_title(service, title, start_datetime, calendar_id='primary'):
    """
    Find and delete an event by its title and start time
    
    Args:
        service: Google Calendar service object
        title: Event title to search for and delete
        start_datetime: Start time in format '2024-01-15T09:00:00'
        calendar_id: Calendar ID to search in (default: 'primary')
    
    Returns:
        Dictionary with deletion result or error info
    """
    try:
        # First, find the event
        find_result = find_event_by_title_and_time(service, title, start_datetime, calendar_id)
        
        if not find_result['success']:
            return find_result
        
        event_id = find_result['event_id']
        event_title = find_result['event_title']
        
        # Now delete the event using the event_id
        delete_result = delete_event(service, event_id, calendar_id)
        
        if delete_result['success']:
            delete_result['message'] = f'Successfully deleted event "{event_title}"'
            delete_result['deleted_event_title'] = event_title
            delete_result['deleted_event_id'] = event_id
        
        return delete_result
        
    except HttpError as error:
        return {
            'success': False,
            'error': str(error),
            'message': 'Failed to find and delete event'
        }


def delete_event(service, event_id, calendar_id='primary'):
    """
    Delete an event by its ID
    
    Args:
        service: Google Calendar service object
        event_id: ID of the event to delete
        calendar_id: Calendar ID where the event exists (default: 'primary')
    
    Returns:
        Dictionary with deletion result or error info
    """
    try:
        # Delete the event
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        
        return {
            'success': True,
            'event_id': event_id,
            'calendar_id': calendar_id,
            'message': f'Event deleted successfully'
        }
        
    except HttpError as error:
        return {
            'success': False,
            'error': str(error),
            'message': 'Failed to delete event'
        }
