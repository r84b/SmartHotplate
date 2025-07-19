# view_models.py

from phases.heat_to import HeatToPhase
from phases.stir_for import StirForPhase

PHASE_VIEWS = {
    HeatToPhase: lambda c: {
        "line1": "Heating",
        "line2": f"{c.heater.get_current_temp():.1f} / {c.heater.target_temp:.1f} °C"
    },
    StirForPhase: lambda c: {
        "line1": "Stirring",
        "line2": f"{c.stirrer.get_current_rpm()} RPM"
    }
}
