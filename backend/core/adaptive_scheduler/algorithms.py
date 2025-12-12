import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ConflictType(Enum):
    TIME_OVERLAP = "time_overlap"
    RESOURCE_CONFLICT = "resource_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"


@dataclass
class ScheduleItem:
    """Represents a scheduled learning item."""
    id: str
    title: str
    duration_minutes: int
    priority: int  # 1-10 scale
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    dependencies: List[str] = field(default_factory=list)  # IDs of prerequisite items
    completed: bool = False
    progress_percentage: float = 0.0


@dataclass
class UserAvailability:
    """Represents user's available time slots."""
    start_time: datetime.datetime
    end_time: datetime.datetime
    confidence: float  # 0-1 scale of how reliable this slot is


class AdaptiveSchedulingAlgorithm:
    """Adaptive scheduling algorithms that adjust based on progress, conflicts, and user availability."""

    def __init__(self, learning_items: List[ScheduleItem], user_availability: List[UserAvailability]):
        self.learning_items = learning_items
        self.user_availability = user_availability
        self.conflicts = []

    def detect_conflicts(self) -> List[Dict]:
        """Detect various types of scheduling conflicts."""
        conflicts = []

        # Sort items by priority and dependencies
        sorted_items = sorted(self.learning_items, key=lambda x: (-x.priority, len(x.dependencies)))

        for i, item1 in enumerate(sorted_items):
            for item2 in sorted_items[i+1:]:
                if self._has_time_overlap(item1, item2):
                    conflicts.append({
                        'type': ConflictType.TIME_OVERLAP,
                        'items': [item1.id, item2.id],
                        'severity': self._calculate_conflict_severity(item1, item2)
                    })

                if self._has_dependency_conflict(item1, item2):
                    conflicts.append({
                        'type': ConflictType.DEPENDENCY_CONFLICT,
                        'items': [item1.id, item2.id],
                        'severity': 9  # High severity for dependency conflicts
                    })

        return conflicts

    def _has_time_overlap(self, item1: ScheduleItem, item2: ScheduleItem) -> bool:
        """Check if two items have overlapping scheduled times."""
        if not item1.start_time or not item1.end_time or not item2.start_time or not item2.end_time:
            return False

        return (item1.start_time < item2.end_time and item1.end_time > item2.start_time)

    def _has_dependency_conflict(self, item1: ScheduleItem, item2: ScheduleItem) -> bool:
        """Check if items have circular or conflicting dependencies."""
        return (item1.id in item2.dependencies and item2.id in item1.dependencies)

    def _calculate_conflict_severity(self, item1: ScheduleItem, item2: ScheduleItem) -> int:
        """Calculate severity of conflict based on priorities and progress."""
        priority_diff = abs(item1.priority - item2.priority)
        progress_avg = (item1.progress_percentage + item2.progress_percentage) / 2

        # Higher severity for conflicts between high-priority items or items with low progress
        severity = (priority_diff / 10) * 5 + ((100 - progress_avg) / 100) * 5
        return min(int(severity), 10)

    def reschedule_based_on_progress(self, item_id: str, new_progress: float) -> List[ScheduleItem]:
        """Adjust schedule based on learning progress changes."""
        item = next((i for i in self.learning_items if i.id == item_id), None)
        if not item:
            return self.learning_items

        old_progress = item.progress_percentage
        item.progress_percentage = new_progress

        # If progress increased significantly, free up time for other items
        if new_progress - old_progress > 20:
            self._optimize_schedule()
        # If progress is slow, allocate more time or reschedule
        elif new_progress < old_progress:
            self._adjust_for_slow_progress(item)

        return self.learning_items

    def reschedule_based_on_availability(self, new_availability: List[UserAvailability]) -> List[ScheduleItem]:
        """Adjust schedule based on updated user availability."""
        self.user_availability = new_availability

        # Find items that no longer fit in available slots
        items_to_reschedule = []
        for item in self.learning_items:
            if item.start_time and item.end_time and not self._is_time_available(item.start_time, item.end_time):
                items_to_reschedule.append(item)

        # Reschedule conflicting items
        for item in items_to_reschedule:
            self._find_best_slot(item)

        return self.learning_items

    def _is_time_available(self, start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
        """Check if a time slot is available in user's schedule."""
        for slot in self.user_availability:
            if (start_time >= slot.start_time and end_time <= slot.end_time):
                return True
        return False

    def _find_best_slot(self, item: ScheduleItem) -> Optional[Tuple[datetime.datetime, datetime.datetime]]:
        """Find the best available time slot for an item."""
        best_slot = None
        best_score = -1

        for slot in self.user_availability:
            slot_duration = (slot.end_time - slot.start_time).total_seconds() / 60

            if slot_duration >= item.duration_minutes:
                # Score based on slot confidence and how well it fits the item
                score = slot.confidence * 10 + (slot_duration - item.duration_minutes) / slot_duration * 5

                if score > best_score:
                    best_score = score
                    start_time = slot.start_time
                    end_time = start_time + datetime.timedelta(minutes=item.duration_minutes)
                    best_slot = (start_time, end_time)

        if best_slot:
            item.start_time, item.end_time = best_slot

        return best_slot

    def _optimize_schedule(self) -> None:
        """Optimize the overall schedule for efficiency."""
        # Sort by priority and dependencies
        self.learning_items.sort(key=lambda x: (-x.priority, len(x.dependencies)))

        # Reset all schedules and reschedule optimally
        for item in self.learning_items:
            if not item.completed:
                self._find_best_slot(item)

    def _adjust_for_slow_progress(self, item: ScheduleItem) -> None:
        """Adjust schedule when progress is slower than expected."""
        # Increase allocated time by 25%
        if item.duration_minutes:
            item.duration_minutes = int(item.duration_minutes * 1.25)

        # Find a better slot if current one is too short
        if item.start_time and item.end_time:
            current_duration = (item.end_time - item.start_time).total_seconds() / 60
            if current_duration < item.duration_minutes:
                self._find_best_slot(item)

    def generate_schedule(self) -> List[ScheduleItem]:
        """Generate an optimized schedule based on all factors."""
        # Detect and resolve conflicts
        conflicts = self.detect_conflicts()
        self._resolve_conflicts(conflicts)

        # Schedule unscheduled items
        for item in self.learning_items:
            if not item.start_time and not item.completed:
                self._find_best_slot(item)

        return self.learning_items

    def _resolve_conflicts(self, conflicts: List[Dict]) -> None:
        """Resolve detected scheduling conflicts."""
        for conflict in sorted(conflicts, key=lambda x: x['severity'], reverse=True):
            if conflict['type'] == ConflictType.TIME_OVERLAP:
                self._resolve_time_overlap(conflict['items'])
            elif conflict['type'] == ConflictType.DEPENDENCY_CONFLICT:
                self._resolve_dependency_conflict(conflict['items'])

    def _resolve_time_overlap(self, item_ids: List[str]) -> None:
        """Resolve time overlap conflicts by rescheduling lower priority items."""
        items = [next(i for i in self.learning_items if i.id == iid) for iid in item_ids]
        items.sort(key=lambda x: x.priority)

        # Reschedule the lower priority item
        if len(items) >= 2:
            lower_priority_item = items[0]
            self._find_best_slot(lower_priority_item)

    def _resolve_dependency_conflict(self, item_ids: List[str]) -> None:
        """Resolve dependency conflicts by adjusting dependencies."""
        # For now, remove circular dependencies
        item1 = next(i for i in self.learning_items if i.id == item_ids[0])
        item2 = next(i for i in self.learning_items if i.id == item_ids[1])

        if item1.id in item2.dependencies:
            item2.dependencies.remove(item1.id)
        if item2.id in item1.dependencies:
            item1.dependencies.remove(item2.id)