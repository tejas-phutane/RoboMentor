"""
Adaptive Scheduling Module

This module provides intelligent scheduling capabilities for learning activities,
integrating with calendar systems and adapting based on user progress and availability.
"""

from .scheduler import AdaptiveScheduler
from .algorithms import AdaptiveSchedulingAlgorithm, ScheduleItem, UserAvailability, ConflictType

__all__ = [
    'AdaptiveScheduler',
    'AdaptiveSchedulingAlgorithm',
    'ScheduleItem',
    'UserAvailability',
    'ConflictType'
]