from utils.pid import TakahashiPID
from equipment.heater.hardware import HeaterHardware
import time

class HeaterController:
    def __init__(self, buzzer, triac_pin=2, overtemp=200.0):
        self._buzzer = buzzer

        self._enabled = True
        self._target_temp = 0
        self._target_hit = False
        self._power_percent = 0.0

        self._error_message = None
        self._failsafe_active = False

        self._last_temp = None
        self._last_update_ms = time.ticks_ms()
        self._failsafe_timer = 0

        self._pid = TakahashiPID(1.514, 44, 11)
        self._overtemp = overtemp

        self.hw = HeaterHardware(triac_pin)

    def enable(self):
        self._enabled = True
        self._failsafe_active = False
        self._error_message = None
        self._failsafe_timer = 0

    def disable(self, reason="unknown"):
        self._enabled = False
        self._error_message = reason
        self.hw.off()

    def set_target_temp(self, temp):
        self._target_temp = temp
        self._target_hit = False
        
    def get_target_temp(self):
        return self._target_temp

    def update(self, temp, plate_temp):
        if not self._enabled or self._failsafe_active:
            self._power_percent = 0
            return

        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last_update_ms) / 1000.0
        self._last_update_ms = now
        
        if temp >= 100:
            self.disable("Overheat")

        if self._target_temp - 1 < temp < self._target_temp + 1 and not self._target_hit:
            self._buzzer.target_reached()
            self._target_hit = True

        error = self._target_temp - temp
        raw_power = self._pid.compute(self._target_temp, temp, dt)
        scaled = round(raw_power / 10, 1)

        if plate_temp >= 150:
            limit = 0.0
        elif error > 15:
            limit = 1.0
        elif 10 < error <= 15:
            limit = 0.7
        elif 5 < error <= 10:
            limit = 0.5
        elif 1 < error <= 5:
            limit = 0.2
        else:
            limit = 0.0

        self._power_percent = min(scaled, limit)
        self.hw.set_power(self._power_percent)


    def get_power(self):
        return self._power_percent

    def get_status(self):
        return {
            "enabled": self._enabled,
            "power_percent": self._power_percent,
            "failsafe": self._failsafe_active,
            "error": self._error_message,
        }

    async def monitor_failsafe(self):
        CHECK = 5
        TIMEOUT = 60
        while True:
            await asyncio.sleep(CHECK)
            if not self._enabled:
                continue
            temp = self._sensor()
            if self._last_temp is None:
                self._last_temp = temp
                continue
            if temp > self._last_temp + 0.2:
                self._last_temp = temp
                self._failsafe_timer = 0
            else:
                self._failsafe_timer += CHECK
            if self._failsafe_timer >= TIMEOUT:
                self._failsafe_active = True
                self.disable("No temperature rise")

    async def pwm_burst_loop(self):
        await self.hw.burst_pwm_driver(lambda: self._power_percent, self.disable)
