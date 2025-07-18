from .base import Phase, PhaseResult
from pid_controller import PID
import time

class HeatTo(Phase):
    def __init__(self, context, target_temp):
        super().__init__(context)
        self.pid = PID(kp=2.0, ki=0.5, kd=0.1, setpoint=target_temp, output_limits=(0, 1))
        self.target = target_temp

    def start(self):
        super().start()

    def update(self):
        current = self.context.read_temp()
        now = time.time()
        duty = self.pid.compute(current, now)

        if current >= self.target:
            self.context.heat_off()
            self.state = PhaseResult.COMPLETE
            return PhaseResult.COMPLETE

        if duty > 0.5:
            self.context.heat_on()
        else:
            self.context.heat_off()
