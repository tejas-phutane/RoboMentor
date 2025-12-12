import datetime
from typing import List, Dict, Optional, Any
from .algorithms import AdaptiveSchedulingAlgorithm, ScheduleItem, UserAvailability, ConflictType
from ...integrations.calendar_integration.google_calendar import GoogleCalendarIntegration


class AdaptiveScheduler:
    """Main adaptive scheduling system that integrates calendar data and learning progress."""

    def __init__(self, calendar_integration: Optional[GoogleCalendarIntegration] = None):
        self.calendar_integration = calendar_integration or GoogleCalendarIntegration()
        self.algorithm = None
        self.scheduled_items: List[ScheduleItem] = []
        self.user_availability: List[UserAvailability] = []

    def initialize_scheduler(self, learning_items: List[Dict[str, Any]]) -> bool:
        """Initialize the scheduler with learning items and user availability."""
        try:
            # Convert dict items to ScheduleItem objects
            self.scheduled_items = []
            for item_data in learning_items:
                item = ScheduleItem(
                    id=item_data['id'],
                    title=item_data['title'],
                    duration_minutes=item_data.get('duration_minutes', 60),
                    priority=item_data.get('priority', 5),
                    dependencies=item_data.get('dependencies', []),
                    completed=item_data.get('completed', False),
                    progress_percentage=item_data.get('progress_percentage', 0.0)
                )
                self.scheduled_items.append(item)

            # Load user availability from calendar
            self._load_user_availability()

            # Initialize the algorithm
            self.algorithm = AdaptiveSchedulingAlgorithm(self.scheduled_items, self.user_availability)

            return True
        except Exception as e:
            print(f"Failed to initialize scheduler: {e}")
            return False

    def _load_user_availability(self) -> None:
        """Load user availability from calendar integration."""
        self.user_availability = []

        if not self.calendar_integration.authenticate():
            # Fallback to default availability if calendar auth fails
            self._set_default_availability()
            return

        # Get current week
        now = datetime.datetime.now(datetime.timezone.utc)
        week_start = now - datetime.timedelta(days=now.weekday())
        week_end = week_start + datetime.timedelta(days=7)

        # Get busy times from calendar
        busy_times = self.calendar_integration.get_free_busy(
            time_min=week_start,
            time_max=week_end
        )

        # Convert busy times to availability (inverse)
        self._calculate_availability_from_busy_times(busy_times, week_start, week_end)

    def _set_default_availability(self) -> None:
        """Set default availability when calendar is not available."""
        now = datetime.datetime.now(datetime.timezone.utc)

        # Default: weekdays 9 AM - 5 PM, weekends 10 AM - 4 PM
        for day_offset in range(7):
            day = now + datetime.timedelta(days=day_offset)
            is_weekend = day.weekday() >= 5

            if is_weekend:
                start_time = datetime.datetime.combine(day.date(), datetime.time(10, 0, tzinfo=datetime.timezone.utc))
                end_time = datetime.datetime.combine(day.date(), datetime.time(16, 0, tzinfo=datetime.timezone.utc))
                confidence = 0.7
            else:
                start_time = datetime.datetime.combine(day.date(), datetime.time(9, 0, tzinfo=datetime.timezone.utc))
                end_time = datetime.datetime.combine(day.date(), datetime.time(17, 0, tzinfo=datetime.timezone.utc))
                confidence = 0.9

            self.user_availability.append(UserAvailability(start_time, end_time, confidence))

    def _calculate_availability_from_busy_times(self, busy_times: List[Dict[str, Any]],
                                               week_start: datetime.datetime,
                                               week_end: datetime.datetime) -> None:
        """Calculate available time slots from busy periods."""
        # This is a simplified implementation
        # In a real system, you'd need more sophisticated logic to handle multiple busy periods

        # For now, assume standard working hours minus busy times
        current_time = week_start
        while current_time < week_end:
            day_end = current_time.replace(hour=17, minute=0, second=0, microsecond=0)
            if current_time.weekday() >= 5:  # Weekend
                day_end = current_time.replace(hour=16, minute=0, second=0, microsecond=0)

            # Check if this time slot conflicts with busy times
            is_available = True
            slot_end = min(current_time + datetime.timedelta(hours=1), day_end)

            for busy_period in busy_times:
                busy_start = datetime.datetime.fromisoformat(busy_period['start'][:-1])  # Remove 'Z'
                busy_end = datetime.datetime.fromisoformat(busy_period['end'][:-1])

                if (current_time < busy_end and slot_end > busy_start):
                    is_available = False
                    break

            if is_available and slot_end > current_time:
                confidence = 0.8 if current_time.weekday() < 5 else 0.6  # Lower confidence on weekends
                self.user_availability.append(UserAvailability(current_time, slot_end, confidence))

            current_time = slot_end

    def generate_schedule(self) -> List[Dict[str, Any]]:
        """Generate an optimized schedule using adaptive algorithms."""
        if not self.algorithm:
            return []

        scheduled_items = self.algorithm.generate_schedule()

        # Convert back to dict format for API response
        return [self._item_to_dict(item) for item in scheduled_items]

    def update_progress(self, item_id: str, new_progress: float) -> List[Dict[str, Any]]:
        """Update learning progress and adjust schedule accordingly."""
        if not self.algorithm:
            return []

        updated_items = self.algorithm.reschedule_based_on_progress(item_id, new_progress)
        return [self._item_to_dict(item) for item in updated_items]

    def update_availability(self, new_availability_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update user availability and reschedule affected items."""
        if not self.algorithm:
            return []

        # Convert dict data to UserAvailability objects
        new_availability = []
        for avail_data in new_availability_data:
            start_time = datetime.datetime.fromisoformat(avail_data['start_time'])
            end_time = datetime.datetime.fromisoformat(avail_data['end_time'])
            confidence = avail_data.get('confidence', 1.0)
            new_availability.append(UserAvailability(start_time, end_time, confidence))

        updated_items = self.algorithm.reschedule_based_on_availability(new_availability)
        return [self._item_to_dict(item) for item in updated_items]

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts."""
        if not self.algorithm:
            return []

        conflicts = self.algorithm.detect_conflicts()

        # Convert conflict types to strings for JSON serialization
        for conflict in conflicts:
            conflict['type'] = conflict['type'].value

        return conflicts

    def create_calendar_event(self, item_id: str) -> bool:
        """Create a calendar event for a scheduled learning item."""
        item = next((i for i in self.scheduled_items if i.id == item_id), None)
        if not item or not item.start_time or not item.end_time:
            return False

        return bool(self.calendar_integration.create_event(
            summary=f"Learning: {item.title}",
            description=f"Scheduled learning session for {item.title}",
            start_time=item.start_time,
            end_time=item.end_time
        ))

    def get_schedule_summary(self) -> Dict[str, Any]:
        """Get a summary of the current schedule."""
        if not self.algorithm:
            return {}

        total_items = len(self.scheduled_items)
        completed_items = len([i for i in self.scheduled_items if i.completed])
        scheduled_items = len([i for i in self.scheduled_items if i.start_time])

        total_scheduled_time = sum(
            (i.end_time - i.start_time).total_seconds() / 60
            for i in self.scheduled_items
            if i.start_time and i.end_time
        )

        conflicts = self.detect_conflicts()

        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'scheduled_items': scheduled_items,
            'total_scheduled_minutes': int(total_scheduled_time),
            'completion_percentage': (completed_items / total_items * 100) if total_items > 0 else 0,
            'conflict_count': len(conflicts),
            'conflicts': conflicts
        }

    def _item_to_dict(self, item: ScheduleItem) -> Dict[str, Any]:
        """Convert ScheduleItem to dictionary."""
        return {
            'id': item.id,
            'title': item.title,
            'duration_minutes': item.duration_minutes,
            'priority': item.priority,
            'start_time': item.start_time.isoformat() if item.start_time else None,
            'end_time': item.end_time.isoformat() if item.end_time else None,
            'dependencies': item.dependencies,
            'completed': item.completed,
            'progress_percentage': item.progress_percentage
        }