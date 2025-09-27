import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz  # You'll need to install this: pip install pytz


def find_events_by_date(service, date_str: str) -> Dict[str, Any]:
    """
    Find all events on a specific date across all calendars
    """
    try:
        print(f"=== FINDING EVENTS FOR DATE: {date_str} ===")
        
        # Parse the date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        print(f"Parsed target date: {target_date}")
        
        # Use UTC timezone for consistency
        utc = pytz.UTC
        
        # Calculate time bounds for the day (start and end of day in UTC)
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # Convert to UTC
        start_datetime_utc = utc.localize(start_datetime)
        end_datetime_utc = utc.localize(end_datetime)
        
        # Convert to RFC3339 format for Google Calendar API
        start_time = start_datetime_utc.isoformat()
        end_time = end_datetime_utc.isoformat()
        
        print(f"Searching for events between {start_time} and {end_time}")
        
        # Get list of all calendars
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        print(f"Found {len(calendars)} calendars to search")
        
        all_events = []
        
        # Search through each calendar
        for calendar in calendars:
            calendar_id = calendar['id']
            calendar_name = calendar.get('summary', 'Unknown Calendar')
            print(f"Searching calendar: {calendar_name} ({calendar_id})")
            
            try:
                # Query events for this calendar
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_time,
                    timeMax=end_time,
                    singleEvents=True,
                    orderBy='startTime',
                    showDeleted=False  # Don't include deleted events
                ).execute()
                
                events = events_result.get('items', [])
                print(f"Found {len(events)} events in {calendar_name}")
                
                # Process each event
                for event in events:
                    # Get event details
                    title = event.get('summary', 'No Title')
                    event_id = event.get('id', 'Unknown ID')
                    
                    print(f"Processing event: {title} (ID: {event_id})")
                    
                    # Get start and end times
                    start = event.get('start', {})
                    end = event.get('end', {})
                    
                    # Handle different time formats
                    if 'dateTime' in start:
                        # Regular events have dateTime
                        start_time_str = start['dateTime']
                        end_time_str = end.get('dateTime', start_time_str)
                        
                        print(f"  Event has dateTime: {start_time_str} to {end_time_str}")
                        
                        # Parse and format times
                        try:
                            start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                            end_dt = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                            
                            # Format times for display
                            start_display = start_dt.strftime('%I:%M %p')
                            end_display = end_dt.strftime('%I:%M %p')
                            
                            print(f"  Formatted times: {start_display} to {end_display}")
                            
                        except Exception as time_error:
                            print(f"  Error parsing times: {time_error}")
                            start_display = "Invalid Time"
                            end_display = "Invalid Time"
                        
                    elif 'date' in start:
                        # All-day events
                        print(f"  Event is all-day")
                        start_display = "All Day"
                        end_display = "All Day"
                    else:
                        print(f"  Event has unknown time format: {start}")
                        start_display = "Unknown Time"
                        end_display = "Unknown Time"
                    
                    # Add to results
                    event_data = {
                        'title': title,
                        'start_time': start_display,
                        'end_time': end_display,
                        'calendar': calendar_name,
                        'calendar_id': calendar_id,
                        'event_id': event_id,
                        'description': event.get('description', ''),
                        'location': event.get('location', ''),
                        'status': event.get('status', 'confirmed'),
                        'created': event.get('created', ''),
                        'updated': event.get('updated', '')
                    }
                    
                    all_events.append(event_data)
                    print(f"  Added event: {event_data}")
                    
            except Exception as calendar_error:
                print(f"Error querying calendar {calendar_name}: {calendar_error}")
                continue
        
        # Sort events by start time
        all_events.sort(key=lambda x: x['start_time'])
        
        print(f"=== FINAL RESULT: Found {len(all_events)} events ===")
        for event in all_events:
            print(f"  - {event['title']} ({event['start_time']} - {event['end_time']}) in {event['calendar']}")
        
        return {
            'message': f'Found {len(all_events)} events on {date_str}',
            'date': date_str,
            'total_events': len(all_events),
            'events': all_events,
            'search_params': {
                'start_time': start_time,
                'end_time': end_time,
                'calendars_searched': len(calendars)
            }
        }
        
    except ValueError as date_error:
        print(f"Date parsing error: {date_error}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")
    except Exception as e:
        print(f"Error finding events: {e}")
        raise HTTPException(status_code=500, detail=f"Error finding events: {str(e)}")