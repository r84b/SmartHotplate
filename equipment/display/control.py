from machine import I2C, Pin
import hardware.sh1106
import time

i2c = I2C(0, scl=Pin(21), sda=Pin(20))
oled = hardware.sh1106.SH1106_I2C(128, 64, i2c)
oled.rotate(True)


def hello():
    oled.fill(0)
    
    # Tekstwaarden
    title = "Smart Heater"
    author = "By Ramon"
    
    # Bereken breedtes om te centreren (128x64 scherm)
    title_x = (128 - len(title)*8) // 2
    author_x = (128 - len(author)*8) // 2
    
    # Titel groter maken door handmatige "bold"
    for y_offset in range(3):  # Fade-in animatie
        oled.fill(0)
        oled.text(title, title_x, 16)
        oled.text(author, author_x, 36)
        oled.show()
        time.sleep(0.1)

    # Simpele fade-in effect
    for i in range(5):
        oled.fill(0)
        oled.text(title, title_x, 16)
        oled.text(author, author_x, 36)
        oled.show()
        time.sleep(0.2)

    time.sleep(2)

    # Scroll effect naar boven
    for shift in range(0, 48, 4):
        oled.fill(0)
        oled.text(title, title_x, 16 - shift)
        oled.text(author, author_x, 36 - shift)
        oled.show()
        time.sleep(0.05)

    oled.fill(0)
    oled.show()

    
def update(temp_plate, temp_external, temp_target, power, rpm, target_rpm, wlan):
    oled.fill(0)
    
    oled.text("Plate: {:.1f}C".format(temp_plate), 0, 0)
    
    if temp_external:
        oled.text("Ext  : {:.1f}C".format(temp_external), 0, 10)
    else:
        oled.text("Ext  : --.-C", 0, 10)
    
    
    oled.text("Target: {:.1f}C".format(temp_target), 0, 20)
    oled.text(f"Rpm: {rpm:.0f}/{target_rpm:.0f}", 0, 40)
    oled.text(f"{wlan.ifconfig()[0]}", 0, 50)
    
    # Power bar direct naast "Power:"
    label_x = 0
    label_y = 30
    oled.text("Power:", label_x, label_y)
    
    bar_x = 50  # naast het woord "Power:"
    bar_y = label_y
    bar_width = int(power * 70)  # max 70 pixels breed
    bar_height = 8

    oled.rect(bar_x, bar_y, 70, bar_height, 1)               # omkadering
    oled.fill_rect(bar_x, bar_y, bar_width, bar_height, 1)   # vulling

    oled.show()
