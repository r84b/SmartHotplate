# phases/hold_and_stir.py

from phases.base import Phase, PhaseResult
import time

class HoldAndStir(Phase):
    def __init__(self, context, target_temp, rpm, duration):
        super().__init__(context)
        self.target = target_temp
        self.rpm = rpm
        self.duration = duration
        self.start_time = None

    def start(self):
        super().start()
        self.context.set_target_temp(self.target)
        self.context.set_target_rpm(self.rpm)
        self.context.heat_on()
        self.start_time = time.time()

    def update(self):
        if time.time() - self.start_time >= self.duration:
            self.context.heat_off()
            self.context.stop_stirrer()
            self.context.buzz_target_reached()
            return PhaseResult.COMPLETE
        return PhaseResult.HOLD
