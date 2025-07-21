# phases/add_ingredient.py

from phases.base import Phase, PhaseResult
import time

class AddIngredient(Phase):
    def __init__(self, context, ingredient=None, timeout=None, wait_for_button=True,):
        """
        label: optionele naam van het ingrediënt (voor display/logging)
        wait_for_button: True = wacht op operator input, False = ga meteen door
        timeout: optionele failsafe (in seconden)
        """
        super().__init__(context)
        self.ingredient = ingredient or "---"
        self.wait_for_button = wait_for_button
        self.timeout = timeout
        self.start_time = None
        self.completed = False

    def start(self):
        super().start()
        self.start_time = time.time()
        self.context.buzz_beep()
        #self.context.set_display_message("ADD", self.label.upper())
        self.context.heat_on()

    def update(self):
        if self.completed:
            return PhaseResult.COMPLETE

        #if self.wait_for_button and self.context.is_button_pressed():
        #    self.completed = True
        #    self.context.buzz_click()
        #    self.context.heat_off()
        #    return PhaseResult.COMPLETE

        if self.timeout and (time.time() - self.start_time >= self.timeout):
            self.completed = True
            self.context.buzz_alarm()
            self.context.heat_off()
            return PhaseResult.COMPLETE

        return PhaseResult.HOLD
