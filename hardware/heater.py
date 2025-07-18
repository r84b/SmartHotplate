import uasyncio as asyncio
from pid import TakahashiPID
from machine import Pin

class HeaterControl:
    def __init__(self, safety_sensor, buzzer, triac_pin = 2, overtemp=200.0):
        self.triac = Pin(triac_pin, Pin.OUT)
        self.triac.off()
        self._power_percent = 0
        self.enabled = True
        self.buzzer = buzzer

        self.safety_sensor = safety_sensor
        self.overtemp_limit = overtemp

        self.last_temp = None
        self.failsafe_timer = 0
        self.failsafe_active = False
        
        self.target_temp = 0
        self.target_hit = False
        
        self.pid = TakahashiPID(1.514, 44, 11)

        self.error_message = None
        self.waiting = False
        
    def set_target_temp(self, temp):
        print(f"Target temp set to: {temp}")
        self.target_temp = temp
        self.target_hit = False

    def set_power(self, percent: float):
        if not self.enabled or self.failsafe_active:
            self._power_percent = 0
            return
        self._power_percent = max(0, min(1, percent))

    def disable(self, reason="unknown"):
        self.enabled = False
        self.triac.off()
        self.error_message = reason
        print(f"[HEATER DISABLED] Reason: {reason}")

    def enable(self):
        self.enabled = True
        self.failsafe_timer = 0
        self.failsafe_active = False
        self.error_message = None
        
    def update(self, current_temp, dt):
        if current_temp > 100:
            heater.disable()
            print(f"Overheating: {temp_plate}")
            return

        if self.waiting and self.target_temp - 1 < current_temp < self.target_temp + 1:
            self.buzzer.target_reached()
            self.waiting = False
            

        error = self.target_temp - current_temp

        raw_power = self.pid.compute(self.target_temp, current_temp, dt)
        power = round(raw_power / 10, 1)

        if error > 15:
            power_limit = 1.0
        elif 10 < error <= 15:
            power_limit = 0.7
        elif 5 < error <= 10:
            power_limit = 0.5
        elif 1 < error <= 5:
            power_limit = 0.2
        else:
            power_limit = 0.0

        self.set_power(min(power, power_limit))

    def get_status(self):
        return {
            "enabled": self.enabled,
            "power_percent": self._power_percent,
            "failsafe": self.failsafe_active,
            "error": self.error_message,
        }

    async def burst_pwm_loop(self):
        WINDOW = 1.0
        STEP = 0.1
        TOTAL_STEPS = int(WINDOW / STEP)

        try:
            while True:
                
                # Safety check
                safety_temp = self.safety_sensor()
                if safety_temp >= self.overtemp_limit:
                    self.disable("Overtemperature")
                    await asyncio.sleep(1)
                    continue

                power = self._power_percent
                steps_on = int(power  * TOTAL_STEPS)
                steps_off = TOTAL_STEPS - steps_on
                print(f"burst on/off {steps_on} {steps_off}")
                # Aan-fase
                for _ in range(steps_on):
                    self.triac.on()
                    await asyncio.sleep(STEP)

                # Uit-fase
            
                for _ in range(steps_off):
                    self.triac.off()
                    await asyncio.sleep(STEP)

        except Exception as e:
            self.disable(f"Burst loop error: {e}")

    async def failsafe_monitor(self, temp_sensor):
        CHECK_INTERVAL = 5
        TIMEOUT = 60

        try:
            while True:
                await asyncio.sleep(CHECK_INTERVAL)
                if not self.enabled:
                    continue

                temp_now = temp_sensor()

                if self.last_temp is None:
                    self.last_temp = temp_now
                    continue

                if temp_now > self.last_temp + 0.2:
                    self.last_temp = temp_now
                    self.failsafe_timer = 0
                else:
                    self.failsafe_timer += CHECK_INTERVAL

                if self.failsafe_timer >= TIMEOUT:
                    self.failsafe_active = True
                    self.disable("No temperature rise")

        except Exception as e:
            self.disable(f"Failsafe loop error: {e}")
