from equipment.heater_control import HeaterControl
from equipment.stirrer.control import StirrerController
from equipment.buzzer.control import Buzzer

class ProcessContext:
    def __init__(self, heater: HeaterControl, stirrer: StirrerController, sensor, buzzer: Buzzer):
        self.heater = heater
        self.stirrer = stirrer
        self.sensor = sensor
        self.buzzer = buzzer

    # Heater interface
    def set_target_temp(self, t):
        self.heater.set_target_temp(t)

    def heat_on(self):
        self.heater.enable()

    def heat_off(self):
        self.heater.disable()

    # Stirrer interface
    def set_target_rpm(self, rpm):
        self.stirrer.set_target_rpm(rpm)

    def stop_stirrer(self):
        self.stirrer.stop()

    def get_rpm(self):
        return self.stirrer.rpm

    def get_stirrer_status(self):
        return self.stirrer.get_status()

    # Buzzer interface
    def buzz_beep(self, frequency=1000, duration=200):
        self.buzzer.beep(frequency, duration)

    def buzz_hum(self, frequency=150, duration=2):
        self.buzzer.hum(frequency, duration)

    def buzz_alarm(self, cycles=5, tone_duration=200, pause_duration=100):
        self.buzzer.alarm(cycles, tone_duration, pause_duration)

    def buzz_pulse_burst(self, duration=1000, on_time=30, off_time=30, frequency=300):
        self.buzzer.pulse_burst(duration, on_time, off_time, frequency)

    def buzz_tick(self):
        self.buzzer.tick()

    def buzz_click(self):
        self.buzzer.click()

    def buzz_target_reached(self):
        self.buzzer.target_reached()

    # System update
    def update_all(self):
        self.heater.update()
        self.stirrer.update()

    # Sensor interface
    def read_temp(self):
        return self.sensor.read_temp()
