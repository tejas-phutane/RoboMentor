"""
Unit tests for Adaptive Scheduler module components.
"""

import pytest
import datetime
from unittest.mock import Mock, patch
from ...core.adaptive_scheduler.algorithms import (
    AdaptiveSchedulingAlgorithm,
    ScheduleItem,
    UserAvailability,
    ConflictType
)
from ...core.adaptive_scheduler.scheduler import AdaptiveScheduler


class TestScheduleItem:
    """Test ScheduleItem dataclass."""

    def test_schedule_item_creation(self):
        """Test creating a schedule item."""
        item = ScheduleItem(
            id="test-1",
            title="Test Learning",
            duration_minutes=60,
            priority=5,
            dependencies=["dep-1"],
            completed=False,
            progress_percentage=25.0
        )

        assert item.id == "test-1"
        assert item.title == "Test Learning"
        assert item.duration_minutes == 60
        assert item.priority == 5
        assert item.dependencies == ["dep-1"]
        assert item.completed is False
        assert item.progress_percentage == 25.0


class TestUserAvailability:
    """Test UserAvailability dataclass."""

    def test_user_availability_creation(self):
        """Test creating user availability."""
        start = datetime.datetime(2024, 1, 1, 9, 0)
        end = datetime.datetime(2024, 1, 1, 17, 0)

        availability = UserAvailability(
            start_time=start,
            end_time=end,
            confidence=0.8
        )

        assert availability.start_time == start
        assert availability.end_time == end
        assert availability.confidence == 0.8


class TestAdaptiveSchedulingAlgorithm:
    """Test adaptive scheduling algorithm."""

    def test_init(self, sample_learning_items):
        """Test algorithm initialization."""
        availability = [
            UserAvailability(
                datetime.datetime(2024, 1, 1, 9, 0),
                datetime.datetime(2024, 1, 1, 17, 0),
                0.8
            )
        ]

        algorithm = AdaptiveSchedulingAlgorithm(sample_learning_items, availability)

        assert len(algorithm.learning_items) == 2
        assert len(algorithm.user_availability) == 1
        assert algorithm.conflicts == []

    def test_detect_conflicts_no_conflicts(self, sample_learning_items):
        """Test conflict detection with no conflicts."""
        availability = [
            UserAvailability(
                datetime.datetime(2024, 1, 1, 9, 0),
                datetime.datetime(2024, 1, 1, 17, 0),
                0.8
            )
        ]

        algorithm = AdaptiveSchedulingAlgorithm(sample_learning_items, availability)
        conflicts = algorithm.detect_conflicts()

        assert len(conflicts) == 0

    def test_detect_time_overlap_conflict(self):
        """Test detecting time overlap conflicts."""
        item1 = ScheduleItem(
            id="item1", title="Task 1", duration_minutes=60, priority=5,
            start_time=datetime.datetime(2024, 1, 1, 10, 0),
            end_time=datetime.datetime(2024, 1, 1, 11, 0)
        )
        item2 = ScheduleItem(
            id="item2", title="Task 2", duration_minutes=60, priority=5,
            start_time=datetime.datetime(2024, 1, 1, 10, 30),
            end_time=datetime.datetime(2024, 1, 1, 11, 30)
        )

        availability = [UserAvailability(
            datetime.datetime(2024, 1, 1, 9, 0),
            datetime.datetime(2024, 1, 1, 17, 0),
            0.8
        )]

        algorithm = AdaptiveSchedulingAlgorithm([item1, item2], availability)
        conflicts = algorithm.detect_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]['type'] == ConflictType.TIME_OVERLAP
        assert conflicts[0]['items'] == ['item1', 'item2']

    def test_detect_dependency_conflict(self):
        """Test detecting dependency conflicts."""
        item1 = ScheduleItem(
            id="item1", title="Task 1", duration_minutes=60, priority=5,
            dependencies=["item2"]
        )
        item2 = ScheduleItem(
            id="item2", title="Task 2", duration_minutes=60, priority=5,
            dependencies=["item1"]
        )

        availability = [UserAvailability(
            datetime.datetime(2024, 1, 1, 9, 0),
            datetime.datetime(2024, 1, 1, 17, 0),
            0.8
        )]

        algorithm = AdaptiveSchedulingAlgorithm([item1, item2], availability)
        conflicts = algorithm.detect_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]['type'] == ConflictType.DEPENDENCY_CONFLICT
        assert conflicts[0]['severity'] == 9

    def test_reschedule_based_on_progress(self):
        """Test rescheduling based on progress changes."""
        item = ScheduleItem(
            id="item1", title="Task 1", duration_minutes=60, priority=5,
            progress_percentage=10.0
        )

        availability = [UserAvailability(
            datetime.datetime(2024, 1, 1, 9, 0),
            datetime.datetime(2024, 1, 1, 17, 0),
            0.8
        )]

        algorithm = AdaptiveSchedulingAlgorithm([item], availability)
        updated_items = algorithm.reschedule_based_on_progress("item1", 40.0)

        assert updated_items[0].progress_percentage == 40.0

    def test_reschedule_based_on_availability(self):
        """Test rescheduling based on availability changes."""
        item = ScheduleItem(
            id="item1", title="Task 1", duration_minutes=60, priority=5,
            start_time=datetime.datetime(2024, 1, 1, 10, 0),
            end_time=datetime.datetime(2024, 1, 1, 11, 0)
        )

        old_availability = [UserAvailability(
            datetime.datetime(2024, 1, 1, 9, 0),
            datetime.datetime(2024, 1, 1, 17, 0),
            0.8
        )]

        new_availability = [UserAvailability(
            datetime.datetime(2024, 1, 1, 12, 0),
            datetime.datetime(2024, 1, 1, 18, 0),
            0.8
        )]

        algorithm = AdaptiveSchedulingAlgorithm([item], old_availability)
        updated_items = algorithm.reschedule_based_on_availability(new_availability)

        # Item should be rescheduled since old slot is no longer available
        assert len(updated_items) == 1

    def test_generate_schedule(self):
        """Test schedule generation."""
        items = [
            ScheduleItem(id="item1", title="Task 1", duration_minutes=60, priority=8),
            ScheduleItem(id="item2", title="Task 2", duration_minutes=45, priority=6)
        ]

        availability = [UserAvailability(
            datetime.datetime(2024, 1, 1, 9, 0),
            datetime.datetime(2024, 1, 1, 17, 0),
            0.8
        )]

        algorithm = AdaptiveSchedulingAlgorithm(items, availability)
        scheduled_items = algorithm.generate_schedule()

        assert len(scheduled_items) == 2
        # Items should be scheduled within availability window
        for item in scheduled_items:
            if item.start_time and item.end_time:
                assert item.start_time >= availability[0].start_time
                assert item.end_time <= availability[0].end_time


class TestAdaptiveScheduler:
    """Test adaptive scheduler main class."""

    def test_init(self):
        """Test scheduler initialization."""
        scheduler = AdaptiveScheduler()
        assert scheduler.algorithm is None
        assert scheduler.scheduled_items == []
        assert scheduler.user_availability == []

    @patch('robomentor_app.backend.core.adaptive_scheduler.scheduler.GoogleCalendarIntegration')
    def test_initialize_scheduler(self, mock_calendar_class, sample_learning_items):
        """Test scheduler initialization with learning items."""
        mock_calendar = Mock()
        mock_calendar.authenticate.return_value = True
        mock_calendar.get_free_busy.return_value = []
        mock_calendar_class.return_value = mock_calendar

        scheduler = AdaptiveScheduler()
        success = scheduler.initialize_scheduler(sample_learning_items)

        assert success is True
        assert scheduler.algorithm is not None
        assert len(scheduler.scheduled_items) == 2

    def test_generate_schedule(self, sample_learning_items):
        """Test schedule generation."""
        scheduler = AdaptiveScheduler()

        # Initialize scheduler
        scheduler.initialize_scheduler(sample_learning_items)

        schedule = scheduler.generate_schedule()
        assert isinstance(schedule, list)

    def test_update_progress(self, sample_learning_items):
        """Test progress update."""
        scheduler = AdaptiveScheduler()
        scheduler.initialize_scheduler(sample_learning_items)

        updated_schedule = scheduler.update_progress("item1", 50.0)
        assert isinstance(updated_schedule, list)

    def test_detect_conflicts(self, sample_learning_items):
        """Test conflict detection."""
        scheduler = AdaptiveScheduler()
        scheduler.initialize_scheduler(sample_learning_items)

        conflicts = scheduler.detect_conflicts()
        assert isinstance(conflicts, list)

    def test_get_schedule_summary(self, sample_learning_items):
        """Test schedule summary generation."""
        scheduler = AdaptiveScheduler()
        scheduler.initialize_scheduler(sample_learning_items)

        summary = scheduler.get_schedule_summary()
        assert isinstance(summary, dict)
        assert "total_items" in summary
        assert "completed_items" in summary
        assert "completion_percentage" in summary