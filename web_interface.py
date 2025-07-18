import network
import uasyncio as asyncio
import json
import hashlib
import binascii
import settings
import api


context = {}  # ontvangt externe verwijzingen zoals main.heater

def set_context(obj):
    global context
    context = obj
    api.set_context(obj)

# === WiFi Config ===
wifi_config = settings.load_settings()["parameters"]["wifi"]
SSID = wifi_config["ssid"]
PASSWORD = wifi_config["pass"]

websocket_clients = []
wlan = None

async def connect_wifi():
    global wlan
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to WiFi...")
    retries = 0
    while not wlan.isconnected() and retries < 30:
        await asyncio.sleep(1)
        retries += 1
        print(f"Waiting for WiFi... {retries}s")

    if wlan.isconnected():
        print("WiFi connected:", wlan.ifconfig())
    else:
        print("WiFi connection failed after timeout.")

html_body = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Status</title>
    <style>
        body { font-family: sans-serif; background: #111; color: #eee; text-align: center; margin-top: 3em; }
        .value { font-size: 3em; margin: 0.5em; }
        .status { font-size: 1em; color: #888; margin: 1em; }
        .connected { color: #4a4; }
        .disconnected { color: #a44; }
        .debug { font-size: 0.8em; color: #666; margin: 1em; text-align: left; max-width: 500px; margin: 1em auto; }
    </style>
</head>
<body>
    <h1>Hotplate Status</h1>
    <div class="status">WebSocket: <span id="ws-status" class="disconnected">Connecting...</span></div>
    
    <div class="value">Temp: <span id="temp">--</span> °C</div>
    <div class="value">RPM: <span id="rpm">--</span></div>

    <div>
        <label>Target Temp:
            <input type="number" id="target-temp" value="0" step="0.5"> °C
            <button onclick="sendTarget()">Set</button>
        </label>
    </div>

    <div>
        <label>Target RPM:
            <input type="number" id="target-rpm" value="0" step="50">
            <button onclick="sendTarget()">Set</button>
        </label>
    </div>

    <div class="debug" id="debug">Starting...</div>

    <script>
        let ws;
        let reconnectTimer;
        let debugEl = document.getElementById('debug');

        function debug(msg) {
            console.log(msg);
            debugEl.innerHTML += msg + '<br>';
            debugEl.scrollTop = debugEl.scrollHeight;
        }

        function connect() {
            debug('Attempting WebSocket connection...');
            const wsUrl = `ws://${window.location.hostname}:80/ws`;
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                debug('WebSocket connected!');
                document.getElementById('ws-status').textContent = 'Connected';
                document.getElementById('ws-status').className = 'connected';
            };

            ws.onmessage = (event) => {
                debug(`Received: ${event.data}`);
                try {
                    const data = JSON.parse(event.data);
                    document.getElementById('temp').textContent = data.temp.toFixed(1);
                    document.getElementById('rpm').textContent = data.rpm;
                } catch (e) {
                    debug(`JSON error: ${e}`);
                }
            };

            ws.onclose = () => {
                document.getElementById('ws-status').textContent = 'Disconnected';
                document.getElementById('ws-status').className = 'disconnected';
                reconnectTimer = setTimeout(connect, 3000);
            };

            ws.onerror = (error) => {
                debug(`WebSocket error: ${error}`);
                document.getElementById('ws-status').textContent = 'Error';
            };
        }

        function sendTarget() {
            const temp = parseFloat(document.getElementById("target-temp").value);
            const rpm = parseInt(document.getElementById("target-rpm").value);

            const message = {
                type: "set",
                target_temp: temp,
                target_rpm: rpm
            };

            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(message));
                debug(`Sent: ${JSON.stringify(message)}`);
            } else {
                debug("WebSocket not connected");
            }
        }

        setTimeout(connect, 100);
    </script>
</body>

</html>
"""

def websocket_hash(key):
    """Generate WebSocket accept hash"""
    WS_MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    key_magic = key + WS_MAGIC_STRING
    hash_obj = hashlib.sha1(key_magic.encode())
    return binascii.b2a_base64(hash_obj.digest()).decode().strip()

def create_websocket_frame(data):
    """Create simple WebSocket frame for sending text data"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    frame = bytearray()
    frame.append(0x81)  # FIN=1, opcode=1 (text)
    
    data_len = len(data)
    if data_len < 126:
        frame.append(data_len)
    else:
        # Voor nu alleen kleine berichten ondersteunen
        frame.append(125)  # Max 125 bytes
        data = data[:125]
    
    frame.extend(data)
    return bytes(frame)

async def handle_websocket(reader, writer):
    """Handle WebSocket connection - simplified version"""
    client_addr = writer.get_extra_info('peername')
    print(f"WebSocket client connected: {client_addr}")
    
    try:
        websocket_clients.append(writer)

        # Start ontvang-loop voor inkomende berichten
        while True:
            header = await reader.read(2)
            if not header or len(header) < 2:
                break

            opcode = header[0] & 0x0F
            payload_len = header[1] & 0x7F

            if payload_len == 126:
                ext = await reader.read(2)
                payload_len = int.from_bytes(ext, 'big')
            elif payload_len == 127:
                ext = await reader.read(8)
                payload_len = int.from_bytes(ext, 'big')

            mask = await reader.read(4)
            masked_data = await reader.read(payload_len)
            data = bytes([masked_data[i] ^ mask[i % 4] for i in range(payload_len)])

            try:
                message = json.loads(data.decode())
                print(f"Received from client: {message}")

                if message.get("type") == "set":
                    if ui_state:
                        ui_state["target_temp"] = float(message.get("target_temp", ui_state.get("target_temp", 0)))
                        ui_state["target_rpm"] = int(message.get("target_rpm", ui_state.get("target_rpm", 0)))
                        print(f"Updated target: temp={ui_state['target_temp']}, rpm={ui_state['target_rpm']}")
            except Exception as e:
                print(f"Failed to process message: {e}")
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print(f"WebSocket client disconnected: {client_addr}")
        if writer in websocket_clients:
            websocket_clients.remove(writer)
        try:
            await writer.aclose()
        except:
            pass

async def serve(reader, writer):
    try:
        # Lees request line
        request_line = await reader.readline()
        if not request_line:
            return
            
        request_str = request_line.decode().strip()
        print(f"Request: {request_str}")
        
        # Lees headers
        headers = {}
        while True:
            header = await reader.readline()
            if header == b"\r\n" or not header:
                break
            header_str = header.decode().strip()
            if ':' in header_str:
                key, value = header_str.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        print(f"Headers: {headers}")
        
        # Parse request
        parts = request_str.split()
        if len(parts) >= 2:
            method = parts[0]
            path = parts[1]
        else:
            method = "GET"
            path = "/"
        
        print(f"Method: {method}, Path: {path}")
        
        # Check for WebSocket upgrade
        if (path == "/ws" and 
            method == "GET" and
            headers.get('upgrade', '').lower() == 'websocket'):
            
            print("WebSocket upgrade requested")
            
            # WebSocket handshake
            ws_key = headers.get('sec-websocket-key')
            if ws_key:
                print(f"WebSocket key: {ws_key}")
                accept_key = websocket_hash(ws_key)
                print(f"Accept key: {accept_key}")
                
                response = "HTTP/1.1 101 Switching Protocols\r\n"
                response += "Upgrade: websocket\r\n"
                response += "Connection: Upgrade\r\n"
                response += f"Sec-WebSocket-Accept: {accept_key}\r\n"
                response += "\r\n"
                
                print("Sending WebSocket handshake response")
                writer.write(response.encode())
                await writer.drain()
                
                # Handle WebSocket connection
                await handle_websocket(reader, writer)
                return
            else:
                print("No WebSocket key found!")
                
        if await api.handle_requests(path, writer, method, headers, reader):
            return
 
        # Regular HTTP request
        if path == "/" or path == "":
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html_body.encode('utf-8'))}\r\n"
            response += "Connection: close\r\n"
            response += "\r\n"
            response += html_body
            print("Serving HTML page")
        else:
            # 404 Not Found
            not_found = "404 Not Found"
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/plain\r\n"
            response += f"Content-Length: {len(not_found)}\r\n"
            response += "Connection: close\r\n"
            response += "\r\n"
            response += not_found
            print(f"404 for path: {path}")
        
        writer.write(response.encode())
        await writer.drain()
        
    except Exception as e:
        print(f"Error in serve: {e}")
        import sys
        sys.print_exception(e)
    finally:
        try:
            await writer.aclose()
        except:
            pass

async def broadcast_status():
    """Broadcast status to all connected WebSocket clients"""
    while True:
        try:
            if websocket_clients:
                status_data = {
                    "temp": context["sensors"].active_temp,
                    "rpm": context["stirrer"].rpm
                }
                message = json.dumps(status_data)
                frame = create_websocket_frame(message)
                
                #print(f"Broadcasting to {len(websocket_clients)} clients: {message}")
                
                # Send to all connected clients
                clients_to_remove = []
                for client in websocket_clients:
                    try:
                        client.write(frame)
                        await client.drain()
                    except Exception as e:
                        print(f"Error sending to client: {e}")
                        clients_to_remove.append(client)
                
                # Remove disconnected clients
                for client in clients_to_remove:
                    if client in websocket_clients:
                        websocket_clients.remove(client)
                        print("Removed disconnected client")
                    
        except Exception as e:
            print(f"Error in broadcast_status: {e}")
            import sys
            sys.print_exception(e)
        
        await asyncio.sleep(1)  # Send updates every second

async def start_server():
    """Start the web server"""
    print("Starting server on port 80...")
    server = await asyncio.start_server(serve, "0.0.0.0", 80)
    print("Server started!")
    print(f"WebSocket clients list initialized: {len(websocket_clients)}")
    
    # Start broadcast task
    asyncio.create_task(broadcast_status())
    print("Broadcast task started")
    
    # Keep server running
    while True:
        await asyncio.sleep(1)

def get_client_count():
    """Get the number of connected WebSocket clients"""
    return len(websocket_clients)

if __name__ == "__main__":
    import sys
    import machine
    import time
    
    print("Web interface standalone mode")
    
    # Main beheert de state objecten
    system_state = {"measured_temp": 42.0, "measured_rpm": 123}
    ui_state = {"mode": "auto", "target_temp": 0.0}
    
    # Geef referenties door aan web interface
    connect_wifi()
    
    # Start server in background
    async def test_main():
        # Start de server
        server_task = asyncio.create_task(start_server())
        
        # Simuleer main loop die direct de state objecten update
        async def simulate_main_loop():
            await asyncio.sleep(5)  # Wacht 5 seconden
            print("Starting main loop simulation...")
            
            for i in range(100):
                # Main update direct zijn eigen state objecten
                temp = 20 + (time.time() % 30)
                rpm = int(100 + (time.time() % 50))
                
                # Direct update van system_state dictionary
                system_state["measured_temp"] = temp
                system_state["measured_rpm"] = rpm
                system_state["timestamp"] = time.time()
                system_state["loop_count"] = i
                
                # Ook UI state kan geupdate worden
                ui_state["last_update"] = time.time()
                ui_state["status"] = "running" if i % 2 == 0 else "measuring"
                
                print(f"Main updated state: temp={temp:.1f}, rpm={rpm}, clients={get_client_count()}")
                await asyncio.sleep(2)
        
        # Start main loop simulatie
        asyncio.create_task(simulate_main_loop())
        
        # Wacht op server
        await server_task
    
    try:
        asyncio.run(test_main())
    except KeyboardInterrupt:
        print("Server stopped")
        sys.exit()