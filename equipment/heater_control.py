import time

class HeaterControl:
    def __init__(self, temp_reader, buzzer=None):
        self._read_temp = temp_reader
        self._buzzer = buzzer
        self._enabled = False
        self._target_temp = 0.0
        self._last_update = time.ticks_ms()
        self._integral = 0.0
        self._last_error = 0.0
        self._output = 0.0

        # PID constants
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.05

        # Heater output interface, e.g. PWM pin or relay control
        self.heater_pin = machine.Pin(5, machine.Pin.OUT)

    def enable(self):
        self._enabled = True
        if self._buzzer:
            self._buzzer.beep(1)

    def disable(self):
        self._enabled = False
        self._output = 0.0
        self.heater_pin.off()

    def set_target_temp(self, temp):
        self._target_temp = temp

    def current_temp(self):
        return self._read_temp()

    def update(self):
        if not self._enabled:
            self.heater_pin.off()
            return

        now = time.ticks_ms()
        dt = (time.ticks_diff(now, self._last_update)) / 1000.0
        if dt <= 0.0:
            return

        self._last_update = now
        current = self.current_temp()
        error = self._target_temp - current

        # PID calculation
        self._integral += error * dt
        derivative = (error - self._last_error) / dt
        self._last_error = error

        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)
        output = max(0.0, min(output, 1.0))  # Clamp between 0-1
        self._output = output

        # Apply output
        self._apply_output(output)

    def _apply_output(self, duty):
        # Simple on/off control; replace with PWM or burst logic if needed
        if duty > 0.5:
            self.heater_pin.on()
        else:
            self.heater_pin.off()

    def is_at_temp(self, threshold=0.5):
        return abs(self._target_temp - self.current_temp()) <= threshold
