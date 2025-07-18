from machine import Pin

class RotaryEncoderHardware:
    def __init__(self, clk_pin, dt_pin, sw_pin):
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        self.last_clk = self.clk.value()
        self.last_button_state = self.sw.value()

    def read_rotation(self):
        clk_state = self.clk.value()
        dt_state = self.dt.value()
        delta = 0

        if clk_state != self.last_clk:
            if dt_state != clk_state:
                delta = 1
            else:
                delta = -1
        self.last_clk = clk_state
        return delta

    def is_pressed(self):
        return self.sw.value() == 0
