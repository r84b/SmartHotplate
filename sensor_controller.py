from hardware.sensors import PT1000Sensor

class SensorController:
    def __init__(self, plate_pin = 27, external_pin = 28):
        
        self.sensor_external = PT1000Sensor(adc_pin=28, v_ref=3.3, r_ref=967)
        self.sensor_plate = PT1000Sensor(adc_pin=27, v_ref=3.3, r_ref=967)
        self.active_temp = None
        
        self.plate_temp = None
        self.external_temp = None
        
    def update(self):
        self.sensor_plate.update()
        
        self.plate_temp = self.sensor_plate.current_temp
        
        self.sensor_external.update()
        self.external_temp = self.sensor_external.current_temp
        
            
        if self.external_temp:
            self.active_temp = self.external_temp
        else:
            self.active_temp = self.plate_temp
