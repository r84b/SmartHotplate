from hardware.sensors import PT1000Sensor
from hardware.heater import HeaterControl
from hardware import display
from hardware.buzzer import Buzzer
from pid_controller import PIDController
from hardware.stirrer import StirrerController
from sensor_controller import SensorController
from pid import TakahashiPID
import uasyncio as asyncio
import utime
import uasyncio as asyncio
#import web_interface
import api

#display.hello()

system_state = {
    "measured_temp": 0.0,
    "measured_rpm": 0
}
ui_state = {
    "target_temp": 0.0,
    "target_rpm": 0
}

# Init state refs
#web_interface.init(system_state, ui_state)

# Start WiFi connectie in de achtergrond
#asyncio.create_task(web_interface.connect_wifi())

buzzer = Buzzer(16)
sensors = SensorController()
heater = HeaterControl(sensors.sensor_plate.read_temperature, buzzer)
stirrer = StirrerController(1, 22)

api.init(sensors)



asyncio.create_task(api.start())


async def main():
    global timer_50ms, timer_100ms, timer_1000ms, timer_2000ms
    global buzzer, stirrer
    
    asyncio.create_task(heater.burst_pwm_loop())
    #asyncio.create_task(heater.failsafe_monitor(sensor_plate.read_temperature))

    # Start webserver
    #asyncio.create_task(web_interface.start_server())
    #asyncio.create_task(api.connect())
    
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

            system_state["measured_temp"] = sensors.active_temp
            system_state["measured_rpm"] = stirrer.rpm
            
            target_temp = ui_state.get("target_temp")
            target_rpm = ui_state.get("target_rpm")
            print(ui_state)
            heater.set_target_temp(target_temp)
            heater.update(sensors.active_temp, dt)
            stirrer.set_target_rpm(target_rpm)

            timer_1000ms = now
        
        if utime.ticks_diff(now, timer_2000ms) > 2000:
            stirrer.measure_rpm()
            stirrer.update()
            
            timer_2000ms = now
        
        if utime.ticks_diff(now, timer_100ms) > 100:
            
            display.update(sensors.plate_temp, sensors.external_temp, heater.target_temp, heater._power_percent, stirrer.rpm, stirrer.target_rpm)
            timer_100ms = now
        
        await asyncio.sleep(0.05)

asyncio.run(main())