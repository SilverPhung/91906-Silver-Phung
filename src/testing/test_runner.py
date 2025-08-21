"""
Test runner for executing tests and managing tracking components.

This module contains the TestRunner class that orchestrates test execution,
    manages active trackers, and generates comprehensive reports.
"""

from typing import Dict, Any, Optional
from src.constants import ENABLE_TESTING
from .centralized_tests import CentralizedTests


class TestRunner:
    """Executes tests and manages tracking components."""

    def __init__(self, game_view):
        self.game_view = game_view
        self.centralized_tests = CentralizedTests(game_view)
        self.active_trackers = {}
        self.test_results = {}

    def run_movement_tests(self) -> Dict[str, Any]:
        """Run all movement tests."""
        if not ENABLE_TESTING:
            return {}

        # Create movement tracker
        movement_tracker = self.centralized_tests.create_movement_tracker()
        self.active_trackers["movement"] = movement_tracker

        # Run tests
        results = {
            "movement_basic": self.centralized_tests.test_player_movement(),
            "movement_speed": self.centralized_tests.test_movement_speed(),
            "collision": self.centralized_tests.test_collision_detection(),
        }

        return results

    def run_combat_tests(self) -> Dict[str, Any]:
        """Run all combat tests."""
        if not ENABLE_TESTING:
            return {}

        # Create combat tracker
        combat_tracker = self.centralized_tests.create_combat_tracker()
        self.active_trackers["combat"] = combat_tracker

        # Run tests
        results = {
            "shooting": self.centralized_tests.test_shooting_mechanics(),
            "bullet_collision": self.centralized_tests.test_bullet_collision(),
            "enemy_damage": self.centralized_tests.test_enemy_damage(),
        }

        return results

    def run_car_tests(self) -> Dict[str, Any]:
        """Run all car interaction tests."""
        if not ENABLE_TESTING:
            return {}

        # Create car tracker
        car_tracker = self.centralized_tests.create_car_tracker()
        self.active_trackers["car"] = car_tracker

        # Run tests
        results = {
            "part_collection": (
                self.centralized_tests.test_car_part_collection()
            ),
            "car_usage": self.centralized_tests.test_car_usage(),
        }

        return results

    def run_health_tests(self) -> Dict[str, Any]:
        """Run all health system tests."""
        if not ENABLE_TESTING:
            return {}

        # Create health tracker
        health_tracker = self.centralized_tests.create_health_tracker()
        self.active_trackers["health"] = health_tracker

        # Run tests
        results = {
            "health_bar": self.centralized_tests.test_health_bar_updates(),
            "damage": self.centralized_tests.test_damage_application(),
        }

        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report."""
        if not ENABLE_TESTING:
            return {}

        all_results = {
            "movement": self.run_movement_tests(),
            "combat": self.run_combat_tests(),
            "car_interaction": self.run_car_tests(),
            "health_system": self.run_health_tests(),
        }

        return self.generate_test_report(all_results)

    def generate_test_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = 0
        passed_tests = 0

        for category, category_results in results.items():
            for test_name, test_result in category_results.items():
                total_tests += 1
                if test_result:
                    passed_tests += 1

        success_rate = (
            (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        )

        report = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "detailed_results": results,
        }

        return report

    def get_tracker_results(
        self, tracker_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get results from a specific tracker."""
        if tracker_name in self.active_trackers:
            tracker = self.active_trackers[tracker_name]
            return tracker.get_results()
        return None

    def get_all_tracker_results(self) -> Dict[str, Any]:
        """Get results from all active trackers."""
        results = {}
        for tracker_name, tracker in self.active_trackers.items():
            results[tracker_name] = tracker.get_results()
        return results

    def clear_trackers(self):
        """Clear all active trackers."""
        self.active_trackers.clear()

    def start_tracking(self, tracker_name: str):
        """Start tracking for a specific component."""
        if tracker_name in self.active_trackers:
            tracker = self.active_trackers[tracker_name]
            if hasattr(tracker, "start_tracking"):
                tracker.start_tracking()

    def record_event(
        self, tracker_name: str, event_type: str, data: Dict[str, Any]
    ):
        """Record an event for a specific tracker."""
        if tracker_name in self.active_trackers:
            tracker = self.active_trackers[tracker_name]
            if hasattr(tracker, f"record_{event_type}"):
                method = getattr(tracker, f"record_{event_type}")
                method(**data)

    def validate_test_results(self, tracker_name: str) -> bool:
        """Validate results from a specific tracker."""
        if tracker_name in self.active_trackers:
            tracker = self.active_trackers[tracker_name]
            results = tracker.get_results()

            # Basic validation based on tracker type
            if tracker_name == "movement":
                return self._validate_movement_results(results)
            elif tracker_name == "combat":
                return self._validate_combat_results(results)
            elif tracker_name == "car":
                return self._validate_car_results(results)
            elif tracker_name == "health":
                return self._validate_health_results(results)

        return False

    def _validate_movement_results(self, results: Dict[str, Any]) -> bool:
        """Validate movement test results."""
        movement_events = results.get("total_movement_events", 0)
        directions_tested = len(results.get("directions_tested", []))
        return movement_events > 0 and directions_tested > 0

    def _validate_combat_results(self, results: Dict[str, Any]) -> bool:
        """Validate combat test results."""
        shots_fired = results.get("shots_fired", 0)
        results.get("hits_landed", 0)
        return shots_fired > 0

    def _validate_car_results(self, results: Dict[str, Any]) -> bool:
        """Validate car interaction test results."""
        interaction_attempts = results.get("interaction_attempts", 0)
        parts_collected = results.get("parts_collected", 0)
        return interaction_attempts > 0 and parts_collected >= 0

    def _validate_health_results(self, results: Dict[str, Any]) -> bool:
        """Validate health test results."""
        health_changes = results.get("total_health_changes", 0)
        return health_changes >= 0
