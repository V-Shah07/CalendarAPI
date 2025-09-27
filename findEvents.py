import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Any


def find_events_by_date(service, date_str: str) -> Dict[str, Any]:
    """
    Find all events on a specific date across all calendars
    """
    try:
        # Parse the date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Calculate time bounds for the day (start and end of day)
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # Convert to RFC3339 format for Google Calendar API
        start_time = start_datetime.isoformat() + 'Z'
        end_time = end_datetime.isoformat() + 'Z'
        
        print(f"Searching for events between {start_time} and {end_time}")
        
        # Get list of all calendars
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        all_events = []
        
        # Search through each calendar
        for calendar in calendars:
            calendar_id = calendar['id']
            calendar_name = calendar.get('summary', 'Unknown Calendar')
            
            try:
                # Query events for this calendar
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_time,
                    timeMax=end_time,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                # Process each event
                for event in events:
                    # Get event details
                    title = event.get('summary', 'No Title')
                    
                    # Get start and end times
                    start = event.get('start', {})
                    end = event.get('end', {})
                    
                    # Handle different time formats
                    if 'dateTime' in start:
                        # All-day events have dateTime
                        start_time_str = start['dateTime']
                        end_time_str = end.get('dateTime', start_time_str)
                        
                        # Parse and format times
                        start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                        
                        # Format times for display
                        start_display = start_dt.strftime('%I:%M %p')
                        end_display = end_dt.strftime('%I:%M %p')
                        
                    elif 'date' in start:
                        # All-day events
                        start_display = "All Day"
                        end_display = "All Day"
                    else:
                        start_display = "Unknown Time"
                        end_display = "Unknown Time"
                    
                    # Add to results
                    all_events.append({
                        'title': title,
                        'start_time': start_display,
                        'end_time': end_display,
                        'calendar': calendar_name,
                        'calendar_id': calendar_id,
                        'event_id': event.get('id'),
                        'description': event.get('description', ''),
                        'location': event.get('location', '')
                    })
                    
            except Exception as calendar_error:
                print(f"Error querying calendar {calendar_name}: {calendar_error}")
                continue
        
        # Sort events by start time
        all_events.sort(key=lambda x: x['start_time'])
        
        return {
            'message': f'Found {len(all_events)} events on {date_str}',
            'date': date_str,
            'total_events': len(all_events),
            'events': all_events
        }
        
    except ValueError as date_error:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")
    except Exception as e:
        print(f"Error finding events: {e}")
        raise HTTPException(status_code=500, detail=f"Error finding events: {str(e)}")