# view_models.py

from phases.heat_to import HeatTo
from phases.stir_for import StirFor

PHASE_VIEWS = {
    HeatTo: lambda c: {
        "line1": "Heating",
        "line2": f"{c.get_current_temp():.1f} / {c.get_target_temp():.1f} °C"
    },
    StirFor: lambda c: {
        "line1": "Stirring",
        "line2": f"{c.get_current_rpm()} RPM"
    }
}
