from enum import Enum, auto

class PhaseState(Enum):
    IDLE = auto()
    RUNNING = auto()
    COMPLETE = auto()
    HELD = auto()
    ABORTED = auto()

class PhaseResult(Enum):
    COMPLETE = auto()
    HOLD = auto()
    ABORT = auto()

class Phase:
    def __init__(self, context):
        self.context = context
        self.state = PhaseState.IDLE

    def start(self):
        self.state = PhaseState.RUNNING

    def update(self):
        raise NotImplementedError
