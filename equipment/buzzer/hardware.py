from machine import PWM, Pin

class BuzzerHardware:
    def __init__(self, pin):
        self.pwm = PWM(pin)

    def set_freq(self, freq):
        self.pwm.freq(freq)

    def on(self, duty=32768):
        self.pwm.duty_u16(duty)

    def off(self):
        self.pwm.duty_u16(0)
