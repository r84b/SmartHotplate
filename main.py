from machine import Pin, PWM, ADC
from time import sleep
from phase_engine import PhaseEngine
from context import ProcessContext
from heater import Heater
from stirrer import Stirrer
from temp_sensor import TempSensor

# Phases
from phases.heat_to import HeatTo
from phases.hold_temp import HoldTemp
from phases.stir_for import StirFor

buzzer = Buzzer(16)
sensors = SensorController()
heater = HeaterControl(sensors.sensor_plate.read_temperature, buzzer)
stirrer = StirrerController(1, 22)
display = DisplayController()  # or whatever your SH1106 wrapper is called
context = ProcessContext(heater, stirrer, sensors)

# Engine
engine = PhaseEngine(context)
engine.add_phase(HeatTo(context, 65.0))
engine.add_phase(HoldTemp(context, 65.0, duration=180))
engine.add_phase(StirFor(context, rpm=500, duration=300))

async def main():
   # Start WiFi connectie in de achtergrond
   asyncio.create_task(web_interface.connect_wifi())
   asyncio.create_task(heater.pwm_burst_loop())
   #asyncio.create_task(heater.monitor_failsafe())

   web_interface.set_context(context)

   # Execution loop
   while True:
      engine.update()
      context.update_all()
      display.update(context)
      await asyncio.sleep(0.5)
       
       
asyncio.run(main())
