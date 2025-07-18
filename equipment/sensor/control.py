from equipment.sensors.hardware import PT1000Sensor

class SensorController:
    def __init__(self, plate_pin=27, external_pin=28):
        self.sensor_plate = PT1000Sensor(adc_pin=plate_pin, v_ref=3.3, r_ref=967)
        self.sensor_external = PT1000Sensor(adc_pin=external_pin, v_ref=3.3, r_ref=967)

        self.plate_temp = None
        self.external_temp = None
        self.active_temp = None

    def update(self):
        self.sensor_plate.update()
        self.plate_temp = self.sensor_plate.current_temp

        self.sensor_external.update()
        self.external_temp = self.sensor_external.current_temp

        if self.external_temp is None:
            self.active_temp = self.plate_temp
        else:
            self.active_temp = self.external_temp

    def read_temp(self):
        return self.active_temp

    def read_plate_temp(self):
        return self.plate_temp

    def read_external_temp(self):
        return self.external_temp
