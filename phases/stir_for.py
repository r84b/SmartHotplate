from phases.base import Phase, PhaseResult
import time

class StirFor(Phase):
    def __init__(self, context, rpm, duration):
        super().__init__(context)
        self.rpm = rpm
        self.duration = duration
        self.start_time = None

    def start(self):
        super().start()
        self.start_time = time.time()
        self.context.set_rpm(self.rpm)

    def update(self):
        if time.time() - self.start_time >= self.duration:
            self.context.stop_stirrer()
            self.state = PhaseResult.COMPLETE
            return PhaseResult.COMPLETE
