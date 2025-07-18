from equipment.heater.control import HeaterControl
from equipment.buzzer.control import Buzzer

class ProcessContext:
    def __init__(self, heater: HeaterControl, stirrer, sensor, buzzer: Buzzer):
        self.heater = heater
        self.stirrer = stirrer
        self.sensor = sensor
        self.buzzer = buzzer

    def set_target_temp(self, t):
        self.heater.set_target_temp(t)

    def heat_on(self):
        self.heater.enable()

    def heat_off(self):
        self.heater.disable()

    def update_all(self):
        self.heater.update()
        # Optional: stirrer.update()

    def read_temp(self):
        return self.sensor.read_temp()

    def buzz_target_reached(self):
        self.buzzer.target_reached()

    def buzz_alarm(self):
        self.buzzer.alarm()

    def buzz_click(self):
        self.buzzer.click()
