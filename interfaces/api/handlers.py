# interfaces/api/handlers.py

import json

context = None

def set_context(ctx):
    global context
    context = ctx

async def _json_response(writer, data):
    body = json.dumps(data)
    writer.write((
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n" +
        body
    ).encode())
    await writer.drain()

async def _bad_request(writer):
    writer.write(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n")
    await writer.drain()

async def _read_body(reader, headers):
    length = int(headers.get("content-length", "0"))
    return (await reader.read(length)).decode().strip() if length > 0 else ""

async def handle_get_temp(writer, reader, headers):
    await _json_response(writer, {
        "plate": context.sensors.plate_temp,
        "external": context.sensors.external_temp
    })

async def handle_get_setpoint(writer, reader, headers):
    await _json_response(writer, {
        "setpoint": context.heater.target_temp
    })

async def handle_post_setpoint(writer, reader, headers):
    try:
        val = float(await _read_body(reader, headers))
        context.heater.set_target_temp(val)
        print(f"Updated setpoint to {context.heater.target_temp}")
        await _json_response(writer, {"setpoint": context.heater.target_temp})
    except Exception as e:
        print("POST error:", e)
        await _bad_request(writer)

async def handle_get_rpm(writer, reader, headers):
    await _json_response(writer, {
        "setpoint": context.stirrer.target_rpm
    })

async def handle_post_rpm(writer, reader, headers):
    try:
        val = int(await _read_body(reader, headers))
        context.stirrer.set_target_rpm(val)
        print(f"Updated target RPM to {context.stirrer.target_rpm}")
        await _json_response(writer, {"setpoint": context.stirrer.target_rpm})
    except Exception as e:
        print("POST error:", e)
        await _bad_request(writer)
        
async def handle_add_phase( writer, reader, headers, engine):

    try:
        body = await _read_body(reader, headers)
        
        data = json.loads(body)
  
        name =  data.get("phase")
        params = data.get("params", {})
        

        engine.add_phase_by_name(name, **params)

        await _json_response(writer, {"setpoint": context})
    except Exception as e:
        print("POST error:", e)
        await _bad_request(writer)
        
async def handle_clear_phases(writer, reader, headers, engine):
    try:
        engine.clear()
        await _json_response(writer, engine.current_phase)
    except Exception as e:
        print("POST error:", e)
        await _bad_request(writer)
        
async def handle_next_phase(writer, reader, headers, engine):
    try:
        engine.start_next()
        await _json_response(writer, engine.current_phase)
    except Exception as e:
        print("POST error:", e)
        await _bad_request(writer)

