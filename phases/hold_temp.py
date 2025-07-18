from .base import Phase, PhaseResult
import time

class HoldTemp(Phase):
    def __init__(self, context, target_temp, duration):
        super().__init__(context)
        self.target = target_temp
        self.duration = duration
        self.start_time = None

    def start(self):
        super().start()
        self.context.set_target_temp(self.target)
        self.context.heat_on()
        self.start_time = time.time()

    def update(self):
        if time.time() - self.start_time >= self.duration:
            self.context.heat_off()
            self.context.buzz_target_reached()
            self.state = PhaseResult.COMPLETE
            return PhaseResult.COMPLETE

        return PhaseResult.RUNNING
