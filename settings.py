import ujson as json

FILENAME = "settings.json"
DEFAULT_SETTINGS = {
    "equipment_module": "HotplateController",
    "parameters": {
        "default_mode": "auto",
        "default_target_temp": 70.0,
        "default_target_rpm": 300,
        "pid": {"kp": 1.2, "ki": 0.01, "kd": 0.5},
        "safety": {"max_temp": 150, "min_temp": 20, "max_rpm": 1200},
        "wifi": {"ssid": "", "pass": ""}
    }
}

def load_settings():
    try:
        with open(FILENAME, "r") as f:
            return json.load(f)
    except:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(FILENAME, "w") as f:
        json.dump(settings, f)

def update_parameter(path, value):
    s = load_settings()
    ref = s["parameters"]
    keys = path.split(".")
    for k in keys[:-1]:
        ref = ref[k]
    ref[keys[-1]] = value
    save_settings(s)


