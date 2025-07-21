# view_models.py

from phases.heat_to import HeatTo
from phases.stir_for import StirFor
from phases.add_ingredient import AddIngredient
from phases.cool_to import CoolTo
from phases.hold_and_stir import HoldAndStir
from phases.hold_temp import HoldTemp

PHASE_VIEWS = {
    HeatTo: lambda c, phase: {
        "line1": "Heating",
        "line2": f"{c.get_current_temp():.1f} / {c.get_target_temp():.1f} °C"
    },
    CoolTo: lambda c, phase: {
        "line1": "Cooling",
        "line2": f"{c.get_current_temp() or 0:.1f} / {c.get_target_temp() or 0:.1f} °C"
    },
    StirFor: lambda c, phase: {
        "line1": "Stirring",
        "line2": f"{c.get_current_rpm()} RPM"
    },
    AddIngredient: lambda c, phase: {
        "line1": "Add Ingredient",
        "line2": f"{phase.ingredient}"
    },
    HoldAndStir: lambda c, phase: {
        "line1": f"Stir {c.get_rpm()}",
        "line2": f"{c.get_current_temp() or 0:.1f} / {c.get_target_temp() or 0:.1f} °C"
    },
    HoldTemp: lambda c, phase: {
        "line1": "Holding Temp",
        "line2": f"{c.get_current_temp() or 0:.1f} / {c.get_target_temp() or 0:.1f} °C"
    }
}

