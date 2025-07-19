# view.py

from equipment.display.control import set_display_lines
from view_models import PHASE_VIEWS

def render(context, phase):
    fn = PHASE_VIEWS.get(type(phase))
    if fn:
        ui_data = fn(context)
    else:
        ui_data = {"line1": "No View", "line2": type(phase).__name__}

    line1 = ui_data.get("line1", "")
    line2 = ui_data.get("line2", "")
    set_display_lines(line1, line2)
