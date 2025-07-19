from equipment.encoder.control import EncoderController

class InputHandler:
    def __init__(self, encoder: EncoderController):
        self.encoder = encoder
        self.mode = "menu"  # or "process"

    def update(self):
        self.encoder.update()

    def is_pressed(self):
        return self.encoder.was_pressed()

    def get_position(self):
        return self.encoder.get_position()

    def reset_position(self):
        self.encoder.position = 0
