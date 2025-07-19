import time
from equipment.stirrer.hardware import StirrerHardware

class StirrerController:
    def __init__(self, pulse_pin_num=1, pwm_pin_num=22, pulses_per_rev=2, pwm_freq=20000):
        self.hw = StirrerHardware(pulse_pin_num, pwm_pin_num, pwm_freq)

        self.pulses_per_rev = pulses_per_rev
        self.target_rpm = 0
        self.duty = 0.0
        self.last_time = time.ticks_ms()
        self.rpm = 0  # Cached value

        self.hw.set_pwm_duty(self.duty)

    def measure_rpm(self):
        now = time.ticks_ms()
        elapsed_ms = time.ticks_diff(now, self.last_time)
        self.last_time = now

        if elapsed_ms <= 0:
            return self.rpm

        pulses = self.hw.reset_pulse_count()
        rotations = pulses / self.pulses_per_rev
        self.rpm = (rotations * 60000) / elapsed_ms
        return self.rpm

    def update(self):
        self.measure_rpm()

        if self.target_rpm == 0:
            self.hw.stop_pwm()
            return

        delta = self.rpm - self.target_rpm
        error_pct = abs(delta) / self.target_rpm

        if error_pct <= 0.02:
            return  # within tolerance

        adjustment = -delta / (2 * self.target_rpm)
        max_step = 0.025
        adjustment = max(-max_step, min(max_step, adjustment))

        self.duty += adjustment
        self.duty = max(0.2, min(1.0, self.duty))

        if self.target_rpm == 0:
            self.duty = 0.0

        self.hw.set_pwm_duty(self.duty)

    def get_target_rpm(self):
        return self.target_rpm

    def set_target_rpm(self, rpm):
        if rpm == 0:
            rpm = 0
        elif rpm < 200:
            rpm = 200
        elif rpm > 1500:
            rpm = 1500

        self.target_rpm = rpm

    def stop(self):
        self.set_target_rpm(0)
        self.hw.stop_pwm()

    def get_status(self):
        return {
            "rpm": self.rpm,
            "target_rpm": self.target_rpm,
            "duty": self.duty
        }
