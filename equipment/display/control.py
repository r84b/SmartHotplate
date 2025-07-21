from machine import I2C, Pin
from equipment.display.hardware import SH1106_I2C
import time


class DisplayController:
    def __init__(self, scl_pin, sda_pin):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.oled = SH1106_I2C(128, 64, self.i2c)
        self.oled.rotate(True)
        self.width = 128
        self.height = 64

    def splash(self):
        self.oled.fill(0)
        title = "Smart Heater"
        author = "By Ramon"
        title_x = (self.width - len(title) * 8) // 2
        author_x = (self.width - len(author) * 8) // 2

        for _ in range(3):
            self.oled.fill(0)
            self.oled.text(title, title_x, 16)
            self.oled.text(author, author_x, 36)
            self.oled.show()
            time.sleep(0.1)

        for _ in range(5):
            self.oled.fill(0)
            self.oled.text(title, title_x, 16)
            self.oled.text(author, author_x, 36)
            self.oled.show()
            time.sleep(0.2)

        time.sleep(2)

        for shift in range(0, 48, 4):
            self.oled.fill(0)
            self.oled.text(title, title_x, 16 - shift)
            self.oled.text(author, author_x, 36 - shift)
            self.oled.show()
            time.sleep(0.05)

        self.oled.fill(0)
        self.oled.show()
        
    def set_lines(self, line1: str, line2: str):
        self.oled.fill(0)
        self.oled.text(line1, 0, 0)
        self.oled.text(line2, 0, 16)
        self.oled.show()


    def update(self, context):
        self.oled.fill(0)

        temp_plate = context.read_plate_temp()
        temp_external = context.read_external_temp()
        temp_target = context.get_target_temp()
        rpm = context.get_rpm()
        target_rpm = context.get_target_rpm()
        power = context.get_power()
        #wlan = context.wlan

        self.oled.text("Plate: {:.1f}C".format(temp_plate), 0, 0)

        if temp_external is not None:
            self.oled.text("Ext  : {:.1f}C".format(temp_external), 0, 10)
        else:
            self.oled.text("Ext  : --.-C", 0, 10)
    
        self.oled.text("Target: {:.1f}C".format(temp_target), 0, 20)
        self.oled.text("Rpm: {:>3}/{:<3}".format(int(rpm), int(target_rpm)), 0, 40)

        #ip = wlan.ifconfig()[0] if wlan else "No WiFi"
        #self.oled.text(ip, 0, 50)

        label_x = 0
        label_y = 30
        self.oled.text("Power:", label_x, label_y)

        bar_x = 50
        bar_y = label_y
        bar_width = int(min(max(power, 0.0), 1.0) * 70)
        bar_height = 8

        self.oled.rect(bar_x, bar_y, 70, bar_height, 1)
        self.oled.fill_rect(bar_x, bar_y, bar_width, bar_height, 1)

        self.oled.show()

