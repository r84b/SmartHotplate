from equipment.heater_control import HeaterControl

class ProcessContext:
    def __init__(self, heater: HeaterControl, stirrer, sensor):
        self.heater = heater
        self.stirrer = stirrer
        self.sensor = sensor

    def set_target_temp(self, t):
        self.heater.set_target_temp(t)

    def heat_on(self):
        self.heater.enable()

    def heat_off(self):
        self.heater.disable()

    def update_all(self):
        self.heater.update()
        # Optional: stirrer.update() if using similar closed-loop control

    def read_temp(self):
        return self.sensor.read_temp()
