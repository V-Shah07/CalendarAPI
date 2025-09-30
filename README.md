# CalendarAPI - Backend for Promptly

Backend API for [Promptly](https://github.com/V-Shah07/Promptly), an agentic AI-powered React Native productivity app.

## What it does

Provides Google Calendar integration for Promptly's intelligent scheduling system. Handles calendar event operations including creating, moving, deleting, and finding events across multiple calendars.

## Tech Stack

- **FastAPI** - Python web framework
- **Google Calendar API v3** - Calendar event management
- **OAuth2** - Authentication with mobile access tokens
- **Railway** - Deployment platform

## Endpoints

- `POST /event/create` - Create new events
- `POST /event/move` - Move existing events
- `POST /event/delete` - Delete events
- `POST /events/find` - Find events by date
- `POST /calendar/create` - Create new calendars

## Integration

This API powers Promptly's autonomous AI scheduling agents, enabling intelligent calendar management and conflict resolution for the mobile app.
