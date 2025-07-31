import arcade
import time
from typing import Dict, Any, Optional
from src.constants import ENABLE_DEBUG, ENABLE_TESTING

class Debug:
    debug_dict = {}
    text_objects = []
    initialized = False
    
    # Testing-related attributes
    testing_objective = None
    test_results = {}
    tracking_events = []
    test_start_time = None

    @staticmethod
    def _initialize():
        if Debug.initialized:
            return

        MAX_DEBUG_LINES = 20
        for i in range(MAX_DEBUG_LINES):
            Debug.text_objects.append(
                arcade.Text(
                    "",
                    0,
                    0,
                    arcade.csscolor.WHITE,
                    18,
                )
            )
        Debug.initialized = True

    @staticmethod
    def update(key: str, text: str):
        Debug.debug_dict[key] = text

    @staticmethod
    def render(x: float, y: float):
        if not ENABLE_DEBUG:
            return

        if not Debug.initialized:
            print("Debug.render called before Debug._initialize. Skipping render.")
            return

        text_object_index = 0
        for key, text_value in Debug.debug_dict.items():
            if text_object_index < len(Debug.text_objects):
                text_object = Debug.text_objects[text_object_index]
                text_object.text = f"{key}: {text_value}"
                text_object.x = x
                text_object.y = y
                text_object.draw()
                y += 20
                text_object_index += 1
            else:
                print(f"Warning: Ran out of pre-allocated debug text objects for key: {key}")

        while text_object_index < len(Debug.text_objects):
            Debug.text_objects[text_object_index].text = ""
            text_object_index += 1
    
    # === Testing Methods ===
    
    @staticmethod
    def set_testing_objective(objective: str):
        """Set the current testing objective."""
        if ENABLE_TESTING:
            Debug.testing_objective = objective
            Debug.test_start_time = time.time()
    
    @staticmethod
    def track_event(event_type: str, data: Dict[str, Any]):
        """Track a testing event."""
        if ENABLE_TESTING:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': time.time()
            }
            Debug.tracking_events.append(event)
    
    @staticmethod
    def validate_test(test_name: str, condition: bool):
        """Validate a test condition."""
        if ENABLE_TESTING:
            Debug.test_results[test_name] = condition
            return condition
        return True
    
    @staticmethod
    def report_test_results():
        """Generate and display test results report."""
        if not ENABLE_TESTING or not Debug.test_results:
            return
        
        total_tests = len(Debug.test_results)
        passed_tests = sum(1 for result in Debug.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': Debug.test_results
        }
    
    @staticmethod
    def clear_testing_data():
        """Clear all testing data."""
        if ENABLE_TESTING:
            Debug.testing_objective = None
            Debug.test_results.clear()
            Debug.tracking_events.clear()
            Debug.test_start_time = None 