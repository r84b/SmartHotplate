# view/view.py

from view.view_models import PHASE_VIEWS

class View:
    def __init__(self, display):
        self.display = display

    def render(self, context, phase):
        if phase is None:
            self.display.set_lines("Idle", "No active phase")
            return

        fn = PHASE_VIEWS.get(type(phase))
        data = fn(context, phase) if fn else {"line1": "?", "line2": type(phase).__name__}
        self.display.set_lines(data.get("line1", ""), data.get("line2", ""))

