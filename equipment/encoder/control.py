from equipment.encoder.hardware import RotaryEncoderHardware
import time

class EncoderController:
    def __init__(self, clk_pin, dt_pin, sw_pin):
        self.hw = RotaryEncoderHardware(clk_pin, dt_pin, sw_pin)
        self.position = 0
        self.pressed = False
        self._last_press_time = 0

    def update(self):
        delta = self.hw.read_rotation()
        self.position += delta

        if self.hw.is_pressed():
            now = time.ticks_ms()
            if time.ticks_diff(now, self._last_press_time) > 300:
                self.pressed = True
                self._last_press_time = now

    def get_position(self):
        return self.position

    def was_pressed(self):
        if self.pressed:
            self.pressed = False
            return True
        return False
