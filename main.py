from hardware.sensors import PT1000Sensor
from hardware.heater import HeaterControl
from hardware import display
from hardware.buzzer import Buzzer
from hardware.stirrer import StirrerController
from sensor_controller import SensorController
from pid import TakahashiPID
import uasyncio as asyncio
import utime
import web_interface

# Start WiFi connectie in de achtergrond
asyncio.create_task(web_interface.connect_wifi())

buzzer = Buzzer(16)
sensors = SensorController()
heater = HeaterControl(sensors.sensor_plate.read_temperature, buzzer)
stirrer = StirrerController(1, 22)

web_interface.set_context({"sensors": sensors, "stirrer": stirrer, "heater": heater})


async def main():
    global timer_50ms, timer_100ms, timer_1000ms, timer_2000ms
    global buzzer, stirrer
    
    asyncio.create_task(heater.burst_pwm_loop())
    #asyncio.create_task(heater.failsafe_monitor(sensor_plate.read_temperature))

    # Start webserver
    asyncio.create_task(web_interface.start_server())
    
    buzzer.beep()

    timer_50ms = utime.ticks_ms()
    timer_100ms = utime.ticks_ms()
    timer_1000ms = utime.ticks_ms()
    timer_2000ms = utime.ticks_ms()

    while True:
        
        now = utime.ticks_ms()
        
        if utime.ticks_diff(now, timer_50ms) > 50:
            sensors.update()
            timer_50ms = now

        if utime.ticks_diff(now, timer_1000ms) > 1000:
       
            dt = utime.ticks_diff(now, timer_1000ms) / 1000
            heater.update(sensors.active_temp, dt)

            timer_1000ms = now
        
        if utime.ticks_diff(now, timer_2000ms) > 2000:
            stirrer.measure_rpm()
            stirrer.update()
            
            timer_2000ms = now
        
        if utime.ticks_diff(now, timer_100ms) > 100:
            
            display.update(sensors.plate_temp, sensors.external_temp, heater.target_temp, heater._power_percent, stirrer.rpm, stirrer.target_rpm, web_interface.wlan)
            timer_100ms = now
        
        await asyncio.sleep(0.05)

asyncio.run(main())