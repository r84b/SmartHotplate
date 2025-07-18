from phases.base import PhaseState, PhaseResult

class PhaseEngine:
    def __init__(self, context):
        self.context = context
        self.queue = []
        self.current_phase = None

    def add_phase(self, phase):
        self.queue.append(phase)

    def start_next(self):
        if self.queue:
            self.current_phase = self.queue.pop(0)
            self.current_phase.start()
        else:
            self.current_phase = None

    def update(self):
        if self.current_phase is None:
            self.start_next()
        elif self.current_phase.state == PhaseState.RUNNING:
            result = self.current_phase.update()
            if result == PhaseResult.COMPLETE:
                self.start_next()
