from phases.base import Phase, PhaseResult

class HeatTo(Phase):
    def __init__(self, context, target_temp):
        super().__init__(context)
        self.target = target_temp

    def start(self):
        super().start()
        self.context.set_target_temp(self.target)
        self.context.heat_on()

    def update(self):
        current = self.context.read_temp()
        if current is None:
            return PhaseResult.HOLD  # of alternatief, zie toelichting onder

        if current >= self.target:
            self.context.heat_off()
            self.context.buzz_target_reached()
            self.state = PhaseResult.COMPLETE
            return PhaseResult.COMPLETE

        return PhaseResult.HOLD  # Gebruik HOLD als 'running' equivalent
