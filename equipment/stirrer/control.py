from machine import Pin, PWM

class StirrerHardware:
    def __init__(self, pulse_pin_num=1, pwm_pin_num=22, pwm_freq=20000):
        self.pulse_count = 0

        self.pulse_pin = Pin(pulse_pin_num, Pin.IN, Pin.PULL_DOWN)
        self.pulse_pin.irq(trigger=Pin.IRQ_RISING, handler=self._count_pulse)

        self.pwm = PWM(Pin(pwm_pin_num))
        self.pwm.freq(pwm_freq)
        self.set_pwm_duty(0)

    def _count_pulse(self, pin):
        self.pulse_count += 1

    def reset_pulse_count(self):
        count = self.pulse_count
        self.pulse_count = 0
        return count

    def set_pwm_duty(self, duty: float):
        duty_u16 = int(65535 * max(0.0, min(1.0, duty)))
        self.pwm.duty_u16(duty_u16)

    def stop_pwm(self):
        self.pwm.duty_u16(0)
