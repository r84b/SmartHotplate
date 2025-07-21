# interfaces/web_interface.py

import uasyncio as asyncio
import network
import json
import hashlib
import binascii

from services import settings
from interfaces.api import routes

def websocket_hash(key):
    magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    digest = hashlib.sha1((key + magic).encode()).digest()
    return binascii.b2a_base64(digest).decode().strip()

def create_websocket_frame(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    data = data[:125]  # truncate if necessary
    frame = bytearray([0x81, len(data)])
    frame.extend(data)
    return bytes(frame)

class WebInterface:
    def __init__(self, context, engine):
        self.context = context
        self.engine = engine
        self.wlan = None
        self.websocket_clients = []

    async def connect_wifi(self):
        cfg = settings.load_settings()["parameters"]["wifi"]
        ssid = cfg.get("ssid", "")
        password = cfg.get("pass", "")

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)

        for retries in range(30):
            if self.wlan.isconnected():
                break
            print(f"WiFi retry {retries + 1}/30...")
            await asyncio.sleep(1)

        if self.wlan.isconnected():
            print("WiFi connected:", self.wlan.ifconfig())
        else:
            print("WiFi failed")

    async def start(self):
        from interfaces.api import handlers
        handlers.set_context(self.context)
        asyncio.create_task(self.broadcast_status())
        server = await asyncio.start_server(self._serve, "0.0.0.0", 80)
        print("Web server running on port 80")
        while True:
            await asyncio.sleep(60)

    async def _serve(self, reader, writer):
        try:
            request = (await reader.readline()).decode().strip()
            headers = {}
            while True:
                line = await reader.readline()
                if line in (b'\r\n', b''):
                    break
                key, _, value = line.decode().partition(':')
                headers[key.lower()] = value.strip()

            method, path = request.split()[:2]

            if path == "/ws" and method == "GET" and headers.get("upgrade", "").lower() == "websocket":
                key = headers.get("sec-websocket-key")
                if not key:
                    return
                accept = websocket_hash(key)
                writer.write((
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
                ).encode())
                await writer.drain()
                await self._handle_ws(reader, writer)
                return

            handler = routes.resolve(method, path)
            if handler:
                await handler(writer, reader, headers, self.engine)
                return

            if path == "/":
                await self._serve_index(writer)
            else:
                await self._serve_404(writer)

        except Exception as e:
            print(f"Serve error: {e}")
        finally:
            try:
                await writer.aclose()
            except:
                pass

    async def _serve_index(self, writer):
        html = self._html_body()
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(html)}\r\n"
            "Connection: close\r\n\r\n"
            f"{html}"
        )
        writer.write(response.encode())
        await writer.drain()

    async def _serve_404(self, writer):
        body = "404 Not Found"
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
            f"{body}"
        )
        writer.write(response.encode())
        await writer.drain()

    async def _handle_ws(self, reader, writer):
        peer = writer.get_extra_info("peername")
        self.websocket_clients.append(writer)
        print(f"WebSocket client: {peer}")

        try:
            while True:
                hdr = await reader.read(2)
                if not hdr or len(hdr) < 2:
                    break
                length = hdr[1] & 0x7F
                if length in (126, 127):
                    break  # skip unsupported extended lengths
                mask = await reader.read(4)
                data = await reader.read(length)
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
                try:
                    msg = json.loads(payload.decode())
                    if msg.get("type") == "set":
                        t = float(msg.get("target_temp", 0))
                        r = int(msg.get("target_rpm", 0))
                        self.context.set_target_temp(t)
                        self.context.set_target_rpm(r)
                except Exception as e:
                    print(f"WS parse error: {e}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            if writer in self.websocket_clients:
                self.websocket_clients.remove(writer)
            try:
                await writer.aclose()
            except:
                pass
            print(f"WebSocket closed: {peer}")

    async def broadcast_status(self):
        while True:
            try:
                if self.websocket_clients:
                    data = {
                        "temp": self.context.read_plate_temp(),
                        "rpm": self.context.get_rpm()
                    }
                    frame = create_websocket_frame(json.dumps(data))
                    for client in self.websocket_clients[:]:
                        try:
                            client.write(frame)
                            await client.drain()
                        except:
                            self.websocket_clients.remove(client)
            except Exception as e:
                print(f"Broadcast error: {e}")
            await asyncio.sleep(1)

    def _html_body(self):
        return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Status</title>
<style>
body{background:#111;color:#eee;font-family:sans-serif;text-align:center;}
.value{font-size:3em;margin:1em;} input{font-size:1em;}
.status{margin:1em;color:#888;}
.connected{color:#4a4;} .disconnected{color:#a44;}
</style></head><body>
<h1>Hotplate</h1>
<div class="status">WebSocket: <span id="ws-status" class="disconnected">Connecting...</span></div>
<div class="value">Temp: <span id="temp">--</span> °C</div>
<div class="value">RPM: <span id="rpm">--</span></div>
<div><input id="target-temp" type="number" step="0.5"> °C <button onclick="setTarget()">Set Temp</button></div>
<div><input id="target-rpm" type="number" step="50"> <button onclick="setTarget()">Set RPM</button></div>
<script>
let ws; function setTarget(){
  let t = parseFloat(document.getElementById("target-temp").value);
  let r = parseInt(document.getElementById("target-rpm").value);
  ws.send(JSON.stringify({type:"set", target_temp:t, target_rpm:r}));
}
function connect(){
  ws = new WebSocket("ws://"+location.hostname+"/ws");
  ws.onopen = () => {
    document.getElementById("ws-status").textContent = "Connected";
    document.getElementById("ws-status").className = "connected";
  }
  ws.onmessage = (e) => {
    let d = JSON.parse(e.data);
    document.getElementById("temp").textContent = d.temp.toFixed(1);
    document.getElementById("rpm").textContent = d.rpm;
  }
  ws.onclose = () => {
    document.getElementById("ws-status").textContent = "Disconnected";
    document.getElementById("ws-status").className = "disconnected";
    setTimeout(connect, 3000);
  }
}
setTimeout(connect, 100);
</script>
</body></html>"""
