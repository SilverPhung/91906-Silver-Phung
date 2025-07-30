import arcade
from src.views.base_view import BaseView
from src.views.game_view import GameView
from src.constants import ENABLE_DEBUG, ENABLE_TESTING, TESTING_OBJECTIVES
from src.managers import TestingManager


class MenuView(BaseView):
    """Class that manages the 'menu' view."""

    def __init__(self):
        super().__init__()
        # Use a more appealing background color
        self.background_color = arcade.color.DARK_GREEN
        
        # Initialize testing manager
        self.testing_manager = TestingManager()
        self.current_objective_index = 0
        self.test_results = None
        
        # Create menu text using the factory with better contrast
        self.menu_text = self.add_centered_text(
            "Zombie Spawn System Testing - Press SPACE to start game, T to cycle objectives, R to run tests",
            y_offset=0,
            color=arcade.color.WHITE,
            font_size=24
        )
        
        # Create testing instruction text
        self.testing_text = self.add_centered_text(
            "",
            y_offset=-50,
            color=arcade.color.YELLOW,
            font_size=20
        )
        
        # Create test results text
        self.results_text = self.add_centered_text(
            "",
            y_offset=-100,
            color=arcade.color.LIGHT_BLUE,
            font_size=16
        )
        
        self.update_instruction_text()
        print("[TESTING] Menu screen loaded - player can start game")

    def on_update(self, dt):
        """Handle transitions when fade_out is set"""
        if self.fade_out is not None:
            self.update_fade(next_view=GameView)

    def on_show_view(self):
        """Called when switching to this view"""
        self.window.background_color = arcade.color.DARK_GREEN

    def on_key_press(self, key, _modifiers):
        """Handle key presses for menu navigation and testing."""
        if self.fade_out is None:
            if key == arcade.key.SPACE:
                print("[TESTING] Player pressed SPACE - starting game")
                self.fade_out = 0
            elif key == arcade.key.T and ENABLE_DEBUG and ENABLE_TESTING:
                # T key cycles through testing objectives
                self.cycle_testing_objective()
            elif key == arcade.key.R and ENABLE_DEBUG and ENABLE_TESTING:
                # R key runs tests
                self.run_current_tests()
    
    def update_instruction_text(self):
        """Update the instruction text based on current testing objective."""
        if ENABLE_DEBUG and ENABLE_TESTING:
            objectives = list(TESTING_OBJECTIVES.keys())
            if objectives:
                current_objective = objectives[self.current_objective_index]
                objective_desc = TESTING_OBJECTIVES[current_objective]
                
                self.testing_text.text = f"Testing: {objective_desc}\nPress T to cycle objectives, R to run tests"
            else:
                self.testing_text.text = "No testing objectives available"
        else:
            self.testing_text.text = ""
    
    def cycle_testing_objective(self):
        """Cycle through available testing objectives."""
        objectives = list(TESTING_OBJECTIVES.keys())
        if objectives:
            self.current_objective_index = (self.current_objective_index + 1) % len(objectives)
            current_objective = objectives[self.current_objective_index]
            self.testing_manager.set_objective(current_objective)
            self.update_instruction_text()
            print(f"[TESTING] Switched to objective: {current_objective}")
    
    def run_current_tests(self):
        """Run tests for the current objective."""
        objectives = list(TESTING_OBJECTIVES.keys())
        if objectives:
            current_objective = objectives[self.current_objective_index]
            print(f"[TESTING] Running tests for objective: {current_objective}")
            
            # Set the objective
            self.testing_manager.set_objective(current_objective)
            
            # Update instruction text
            self.update_instruction_text()
            
            # Show test execution message
            self.results_text.text = f"Tests will run when game starts..."
            print("[TESTING] Tests queued for execution when game starts")
    
    def display_test_results(self, results):
        """Display test results on the menu."""
        if results and ENABLE_DEBUG and ENABLE_TESTING:
            total_tests = results.get('total_tests', 0)
            passed_tests = results.get('passed_tests', 0)
            success_rate = results.get('success_rate', 0)
            
            self.results_text.text = f"Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)"
            print(f"[TESTING] Displaying test results: {passed_tests}/{total_tests} passed")
        else:
            self.results_text.text = ""

    def setup(self):
        """This should set up your game and get it ready to play"""
        pass 