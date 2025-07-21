from equipment.buzzer.control import BuzzerController
from equipment.heater.control import HeaterController
from equipment.sensor.control import SensorController
from equipment.stirrer.control import StirrerController
import time

class ProcessContext:
    def __init__(self, heater: HeaterController, stirrer: StirrerController, sensors: SensorController, buzzer: BuzzerController):
        self.heater = heater
        self.stirrer = stirrer
        self.sensors = sensors
        self.buzzer = buzzer
        
        self._last_sensor = time.ticks_ms()
        self._last_stirrer = self._last_sensor
        self._last_heater = self._last_sensor

    # Heater interface
    def get_target_temp(self):
        return self.heater.get_target_temp()
        
    def set_target_temp(self, t):
        self.heater.set_target_temp(t)

    def heat_on(self):
        self.heater.enable()

    def heat_off(self):
        self.heater.disable()
    
    def get_power(self):
        return self.heater.get_power()

    # Stirrer interface
    def set_target_rpm(self, rpm):
        self.stirrer.set_target_rpm(rpm)
        
    def get_target_rpm(self):
        return self.stirrer.get_target_rpm()

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

    # Sensor interface
    def get_current_temp(self):
        return self.sensors.get_current_temp()

    def read_plate_temp(self):
        return self.sensors.read_plate_temp()

    def read_external_temp(self):
        return self.sensors.read_external_temp()

    # System update

    def update_all(self):
        now = time.ticks_ms()

        if time.ticks_diff(now, self._last_sensor) >= 50:
            self.sensors.update()
            self._last_sensor = now

        if time.ticks_diff(now, self._last_stirrer) >= 500:
            self.stirrer.update()
            self._last_stirrer = now

        if time.ticks_diff(now, self._last_heater) >= 1000:
            t = self.get_current_temp()
            p = self.read_plate_temp()
            self.heater.update(t, p)
            self._last_heater = now
        
        
