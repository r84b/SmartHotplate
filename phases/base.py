# Simuleer enums als constante klassen
class PhaseState:
    IDLE = 0
    RUNNING = 1
    COMPLETE = 2
    HELD = 3
    ABORTED = 4

class PhaseResult:
    COMPLETE = 0
    HOLD = 1
    ABORT = 2

class Phase:
    def __init__(self, context):
        self.context = context
        self.state = PhaseState.IDLE

    def start(self):
        self.state = PhaseState.RUNNING

    def update(self):
        raise NotImplementedError
