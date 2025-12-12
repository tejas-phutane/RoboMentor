"""
Calendar Integration Module

This module provides integration with external calendar services,
currently supporting Google Calendar OAuth2 authentication and event management.
"""

from .google_calendar import GoogleCalendarIntegration

__all__ = ['GoogleCalendarIntegration']