# phases/cool_to.py

from phases.base import Phase, PhaseResult

class CoolTo(Phase):
    def __init__(self, context, target_temp):
        super().__init__(context)
        self.target = target_temp

    def start(self):
        super().start()
        self.context.heat_off()  # garandeer passieve afkoeling
        self.context.set_target_temp(self.target)  # optioneel: doel wissen
        self.context.buzz_beep()

    def update(self):
        current = self.context.get_current_temp()
        if current is None:
            return PhaseResult.HOLD

        if current <= self.target:
            self.context.buzz_target_reached()
            self.state = PhaseResult.COMPLETE
            return PhaseResult.COMPLETE

        return PhaseResult.HOLD
