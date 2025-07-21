# interfaces/api/routes.py

from interfaces.api import handlers

ROUTES = {
    ("GET", "/temp"): handlers.handle_get_temp,
    ("GET", "/setpoint"): handlers.handle_get_setpoint,
    ("POST", "/setpoint"): handlers.handle_post_setpoint,
    ("GET", "/target_rpm"): handlers.handle_get_rpm,
    ("POST", "/target_rpm"): handlers.handle_post_rpm,
    ("POST", "/add_phase"): handlers.handle_add_phase
}

def resolve(method, path):
    return ROUTES.get((method.upper(), path))
