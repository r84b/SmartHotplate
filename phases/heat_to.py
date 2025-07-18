from .base import Phase, PhaseResult

class HeatTo(Phase):
    def __init__(self, context, target_temp):
        super().__init__(context)
        self.target = target_temp

    def start(self):
        super().start()

    def update(self):
        current = self.context.read_temp()
        if current >= self.target:
            self.context.heat_off()
            self.state = PhaseResult.COMPLETE
            return PhaseResult.COMPLETE
        self.context.heat_on()
