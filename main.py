from machine import Pin, PWM, ADC
from time import sleep
from context.process_context import ProcessContext
from engine.phase_engine import PhaseEngine
from equipment.buzzer.control import BuzzerController
from equipment.display.control import DisplayController
from equipment.heater.control import HeaterController
from equipment.sensor.control import SensorController
from equipment.stirrer.control import StirrerController
from interfaces.ui_state_manager import UIStateManager
from interfaces.web_interface import WebInterface
from services import settings 
import uasyncio as asyncio
from view.view import View

# Phases
from phases.heat_to import HeatTo
from phases.hold_temp import HoldTemp
from phases.stir_for import StirFor

buzzer = BuzzerController(16)
sensors = SensorController()
heater = HeaterController(buzzer, 2)
stirrer = StirrerController(1, 22)
display = DisplayController(scl_pin=21, sda_pin=20)  # or whatever your SH1106 wrapper is called
context = ProcessContext(heater, stirrer, sensors, buzzer)
view = View(display)



# Engine
engine = PhaseEngine(context)
#engine.add_phase(HeatTo(context, 65.0))
#engine.add_phase(HoldTemp(context, 65.0, duration=180))
#engine.add_phase(StirFor(context, rpm=500, duration=300))

web_interface = WebInterface(context, engine)

async def main():
    # Start WiFi connectie in de achtergrond
    await web_interface.connect_wifi()
    asyncio.create_task(web_interface.start())

    asyncio.create_task(sensors.run_loop())
    asyncio.create_task(heater.pwm_burst_loop())
    #asyncio.create_task(heater.monitor_failsafe())

    #display.splash()
    #buzzer.beep()

    # Execution loop
    while True:
      context.update_all()
      engine.update()
      
      view.render(context, engine.current_phase)
        
      await asyncio.sleep(0.05)
       
       
asyncio.run(main())
