class ProcessContext:
    def __init__(self, heater, stirrer, sensor):
        self.heater = heater
        self.stirrer = stirrer
        self.sensor = sensor

    def read_temp(self):
        return self.sensor.read_temp()

    def heat_on(self):
        self.heater.enable()

    def heat_off(self):
        self.heater.disable()

    def set_rpm(self, rpm):
        self.stirrer.set_rpm(rpm)

    def stop_stirrer(self):
        self.stirrer.stop()
