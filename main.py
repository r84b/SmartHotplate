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
import asyncio

# Phases
from phases.heat_to import HeatTo
from phases.hold_temp import HoldTemp
from phases.stir_for import StirFor

buzzer = BuzzerController(16)
sensors = SensorController()
heater = HeaterController(buzzer, 2)
stirrer = StirrerController(1, 22)
display = DisplayController()  # or whatever your SH1106 wrapper is called
context = ProcessContext(heater, stirrer, sensors, buzzer)
web_interface = WebInterface(context)


# Engine
engine = PhaseEngine(context)
engine.add_phase(HeatTo(context, 65.0))
engine.add_phase(HoldTemp(context, 65.0, duration=180))
engine.add_phase(StirFor(context, rpm=500, duration=300))

async def main():
    # Start WiFi connectie in de achtergrond
    asyncio.create_task(web_interface.connect_wifi())

    asyncio.create_task(sensors.run_loop())
    asyncio.create_task(heater.pwm_burst_loop())
    #asyncio.create_task(heater.monitor_failsafe())

    #display.splash()
    #buzzer.beep()

    # Execution loop
    while True:
      engine.update()
      context.update_all()

      display.update(context)
      await asyncio.sleep(0.5)
       
       
asyncio.run(main())
