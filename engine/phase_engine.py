from phases.base import PhaseState, PhaseResult
from phases.heat_to import HeatTo
from phases.hold_temp import HoldTemp
from phases.stir_for import StirFor
from phases.hold_and_stir import HoldAndStir
from phases.add_ingredient import AddIngredient
from phases.cool_to import CoolTo


class PhaseEngine:
    def __init__(self, context):
        self.context = context
        self.queue = []
        self.current_phase = None
        
        self.phase_registry = {
            "heat_to": HeatTo,
            "hold_temp": HoldTemp,
            "stir_for": StirFor,
            "add_ingredient": AddIngredient,
            "hold_and_stir": HoldAndStir,
            "cool_to": CoolTo
        }
        
    def add_phase_by_name(self, name, **params):
        cls = self.phase_registry.get(name.lower())
        if not cls:
            raise ValueError(f"Unknown phase '{name}'")
        phase = cls(self.context, **params)
        self.add_phase(phase)

    def add_phase(self, phase):
        self.queue.append(phase)

    def start_next(self):
        if self.queue:
            self.current_phase = self.queue.pop(0)
            self.current_phase.start()
        else:
            self.current_phase = None
            
    def clear(self):
        self.current_phase = None
        self.queue.clear()

    def update(self):
        if self.current_phase is None:
            self.start_next()
        elif self.current_phase.state == PhaseState.RUNNING:
            result = self.current_phase.update()
            if result == PhaseResult.COMPLETE:
                self.start_next()

