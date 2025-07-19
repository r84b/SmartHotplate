from interfaces.input_handler import InputHandler
from equipment.display.control import DisplayController

class UIStateManager:
    def __init__(self, input_handler: InputHandler, display: DisplayController):
        self.input_handler = input_handler
        self.display = display
        self.state = "status"  # options: "status", "menu", "confirm"
        self.menu_index = 0
        self.max_menu_items = 3  # adjust as needed

    def set_state(self, state: str):
        self.state = state
        if state == "menu":
            self.menu_index = 0
        self.render()

    def update(self):
        self.input_handler.update()

        if self.state == "menu":
            delta = self.input_handler.encoder.get_position()
            if delta != 0:
                self.menu_index = max(0, min(self.menu_index + delta, self.max_menu_items - 1))
                self.render()

        elif self.state == "confirm":
            if self.input_handler.encoder.was_pressed():
                self.display.clear()
                self.state = "status"
                return "confirmed"

        return None

    def render(self):
        if self.state == "menu":
            self.display.show_menu(self.menu_index)

        elif self.state == "confirm":
            self.display.show_message("Press to continue")

    def sync_with_context(self, context, phase_name):
        if self.state != "status":
            return

        self.display.show_status(
            temp_plate=context.read_plate_temp(),
            temp_external=context.read_external_temp(),
            temp_target=context.heater.target_temp,
            power=context.heater.get_output_power(),
            rpm=context.stirrer.rpm,
            target_rpm=context.stirrer.target_rpm,
            wlan=context.network_interface,
            phase=phase_name
        )
