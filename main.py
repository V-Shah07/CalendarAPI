from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Import your existing functions
from createEvent import add_event
from createCalendar import create_calendar  
from moveEvent import move_event_by_title, find_event_by_title_and_time
from findEvents import find_events_by_date

# Create security scheme
security = HTTPBearer()

app = FastAPI(title="Google Calendar API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CreateEventRequest(BaseModel):
    title: str
    start_datetime: str
    end_datetime: str
    description: Optional[str] = ""
    calendar_id: Optional[str] = 'primary'

class CreateCalendarRequest(BaseModel):
    calendar_name: str
    description: Optional[str] = ""

class MoveEventRequest(BaseModel):
    title: str
    current_start_datetime: str
    new_start_datetime: str
    new_end_datetime: str
    calendar_id: Optional[str] = 'primary'

class FindEventRequest(BaseModel):
    title: str
    start_datetime: str
    calendar_id: Optional[str] = 'primary'

class FindEventsRequest(BaseModel):
    date: str  # YYYY-MM-DD format

# Modified authentication function for mobile tokens
def authenticate_with_token(access_token: str):
    """Authenticate using access token from mobile app"""
    try:
        print(f"Authenticating with token: {access_token[:20]}...")
        
        # Create credentials object from access token
        # For mobile tokens, we don't have refresh capabilities, so we set refresh_token to None
        creds = Credentials(
            token=access_token,
            refresh_token=None,
            token_uri=None,
            client_id=None,
            client_secret=None
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=creds)
        
        # Test the credentials by making a simple API call
        try:
            # Try to get calendar list to verify the token works
            calendars_result = service.calendarList().list().execute()
            print(f"Authentication successful, found {len(calendars_result.get('items', []))} calendars")
        except Exception as test_error:
            print(f"Token validation failed: {test_error}")
            raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(test_error)}")
        
        return service
    except HTTPException:
        raise
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Dependency to get service from authorization header
async def get_calendar_service(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract token from Authorization header and create service"""
    token = credentials.credentials
    return authenticate_with_token(token)

@app.get("/")
async def root():
    return {"message": "Google Calendar API Server is running"}

@app.post("/calendar/create")
async def create_calendar_endpoint(
    request: CreateCalendarRequest,
    service = Depends(get_calendar_service)
):
    """Create a new calendar"""
    try:
        result = create_calendar(service, request.calendar_name, request.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/event/create")
async def create_event_endpoint(
    request: CreateEventRequest,
    service = Depends(get_calendar_service)
):
    """Create a new event"""
    try:
        result = add_event(
            service, 
            request.title, 
            request.start_datetime, 
            request.end_datetime, 
            request.description,
            request.calendar_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/event/move")
async def move_event_endpoint(
    request: MoveEventRequest,
    service = Depends(get_calendar_service)
):
    """Move an existing event"""
    try:
        result = move_event_by_title(
            service,
            request.title,
            request.current_start_datetime,
            request.new_start_datetime,
            request.new_end_datetime,
            request.calendar_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/find")
async def find_events_endpoint(
    request: FindEventsRequest,
    service = Depends(get_calendar_service)
):
    """Find all events on a specific date across all calendars"""
    try:
        result = find_events_by_date(service, request.date)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/events/find")
async def find_events_endpoint(
    request: FindEventsRequest,
    service = Depends(get_calendar_service)
):
    """Find all events on a specific date across all calendars"""
    try:
        result = find_events_by_date(service, request.date)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)