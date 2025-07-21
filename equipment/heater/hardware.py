import uasyncio as asyncio
from machine import Pin

class HeaterHardware:
    def __init__(self, pin_number):
        self._triac = Pin(pin_number, Pin.OUT)
        self._triac.off()

    def set_power(self, power):
        self._last_power = max(0.0, min(1.0, power))

    def off(self):
        self._triac.off()

    async def burst_pwm_driver(self, power_reader, disable_callback):
        STEP = 0.1
        WINDOW = 1.0
        TOTAL = int(WINDOW / STEP)
        while True:

            power = power_reader()
            on_steps = int(power * TOTAL)
            off_steps = TOTAL - on_steps

            for _ in range(on_steps):
                self._triac.on()
                await asyncio.sleep(STEP)
            for _ in range(off_steps):
                self._triac.off()
                await asyncio.sleep(STEP)
