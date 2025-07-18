from machine import Pin, PWM
import time

class StirrerController:
    def __init__(self, pulse_pin_num=1, pwm_pin_num=22, pulses_per_rev=2, pwm_freq=20000):
        self.pulses_per_rev = pulses_per_rev
        self.target_rpm = 0
        self.duty = 0.0
        self.last_time = time.ticks_ms()
        self.pulse_count = 0
        self.rpm = 0  # ← opgeslagen waarde van laatst gemeten RPM

        # Setup pulse input pin with interrupt
        self.pulse_pin = Pin(pulse_pin_num, Pin.IN, Pin.PULL_DOWN)
        self.pulse_pin.irq(trigger=Pin.IRQ_RISING, handler=self._count_pulse)

        # Setup PWM output
        self.pwm = PWM(Pin(pwm_pin_num))
        self.pwm.freq(pwm_freq)
        self.set_duty(self.duty)

    def _count_pulse(self, pin):
        self.pulse_count += 1

    def set_duty(self, duty):
        self.duty = max(0.0, min(1.0, duty))  # constrain dutycycle
        self.pwm.duty_u16(int(65535 * self.duty))

    def measure_rpm(self):
        now = time.ticks_ms()
        elapsed_ms = time.ticks_diff(now, self.last_time)
        self.last_time = now

        if elapsed_ms <= 0:
            return self.rpm  # return previous if invalid timing

        pulses = self.pulse_count
        self.pulse_count = 0

        rotations = pulses / self.pulses_per_rev
        self.rpm = (rotations * 60000) / elapsed_ms  # store rpm
        return self.rpm

    def update(self):
        if self.target_rpm == 0:
            self.pwm.duty_u16(0)
            return

        delta = self.rpm - self.target_rpm
        error_pct = abs(delta) / self.target_rpm

        # Stop aanpassen als binnen 2% marge
        if error_pct <= 0.02:
            return  # binnen tolerantie, niets doen

        # Bepaal correctiefactor: kleiner verschil = kleinere stap
        adjustment = -delta / (2 * self.target_rpm)  # afzwakken
        max_step = 0.025

        # Clamp de correctie
        adjustment = max(-max_step, min(max_step, adjustment))

        # Pas toe
        self.duty += adjustment
        self.duty = max(0.0, min(1.0, self.duty))  # houd binnen bereik

        self.set_duty(self.duty)

    def get_status(self):
        return {
            "rpm": self.rpm,
            "target_rpm": self.target_rpm,
            "duty": self.duty
        }

    def set_target_rpm(self, rpm):
        
        if rpm == 0:
            rpm = 0
        elif rpm < 200:
            rpm = 200
        elif rpm > 1500:
            rpm = 1500
            
        self.target_rpm = rpm
