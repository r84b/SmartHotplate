import network
import picoweb
import ujson
import uasyncio as asyncio
from ujson import dumps

sensors = None  # globale placeholder

def init(sensor_ref):
    global sensors
    sensors = sensor_ref
    print("[API] sensors gekoppeld:", sensors)

# ✅ Async WiFi connectie
async def connect_wifi(ssid="", password=""):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Connecting to WiFi...")
    for i in range(30):  # 30s timeout
        if wlan.isconnected():
            print("Connected:", wlan.ifconfig())
            return True
        await asyncio.sleep(1)
    print("Failed to connect to WiFi.")
    return False

# 🌐 WebApp
app = picoweb.WebApp(__name__)
status = {"led": False, "temp": 25.5}

@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Welcome to the Pico API!")

@app.route("/status")
def api_status(req, resp):
    yield from picoweb.start_response(resp, "application/json")
    yield from resp.awrite(ujson.dumps(status))
    
@app.route("/temp", methods=["GET"])
def api_temp_get(req, resp):
    yield from picoweb.start_response(resp, "application/json")
    try:
        temp = sensors.active_temp  # zorg dat dit een float is
    except:
        temp = 0.0  # fallback als sensors nog niet klaar is

    yield from resp.awrite(dumps({"temp": round(temp, 2)}))

@app.route("/temp", methods=["POST"])
def api_temp_set(req, resp):
    print(req, resp)
    yield from req.read_form_data()
    form = req.form

    try:
        if b"value" in form:
            setpoint = float(form[b"value"])
            status["temp"] = setpoint
            print("[API] Nieuwe setpoint:", setpoint)
            result = {"ok": True, "setpoint": setpoint}
        else:
            result = {"ok": False, "error": "Missing 'value'"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    yield from picoweb.start_response(resp, "application/json")
    yield from resp.awrite(ujson.dumps(result))



# 🚀 Async main()
async def start():
    connected = await connect_wifi()
    if not connected:
        return
    await asyncio.sleep(1)
    app.run(debug=True, host="0.0.0.0", port=80)
    
def main():
    app.run(debug=True, host="0.0.0.0", port=80)
    
main()
