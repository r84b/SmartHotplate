import json

context = {}  # ontvangt externe verwijzingen zoals main.heater

def set_context(obj):
    global context
    context = obj


async def handle_requests(path, writer, method, headers, reader):
    
    async def send_json_response(data, label):
        body = json.dumps(data)
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += body
        print(f"Serving {label} endpoint")
        writer.write(response.encode())
        await writer.drain()
        
    async def read_plain_body():
        length = int(headers.get("content-length", "0"))
        if length > 0:
            raw = await reader.read(length)
            return raw.decode().strip()
        return ""
        
    if path == "/temp" and method == "GET":
        await send_json_response({"plate": context["sensors"].plate_temp, "external": context["sensors"].external_temp}, "/temp")
        return True

    if path == "/setpoint" and method == "GET":
        await send_json_response({"setpoint": context["heater"].target_temp}, "/setpoint")
        return True
    
    if path == "/setpoint" and method == "POST":
        try:
            body = await read_plain_body()
            context["heater"].set_target_temp(float(body))
            print(f"Updated setpoint to {context["heater"].target_temp}")
            await send_json_response(
                {"setpoint": context["heater"].target_temp},
                "/setpoint POST"
            )
            return True
        except Exception as e:
            print("POST parse error:", e)
            response = "HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n"
            writer.write(response.encode())
            await writer.drain()
            return True

    if path == "/target_rpm" and method == "GET":
            await send_json_response({"setpoint": context["stirrer"].target_rpm}, "/setpoint")
            return True
        
    if path == "/target_rpm" and method == "POST":
        try:
            body = await read_plain_body()
            context["stirrer"].set_target_rpm(int(body))
            print(f"Updated target RPM to {context["stirrer"].target_rpm}")
            await send_json_response(
                {"setpoint": context["stirrer"].target_rpm},
                "/setpoint POST"
            )
            return True
        except Exception as e:
            print("POST parse error:", e)
            response = "HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n"
            writer.write(response.encode())
            await writer.drain()
            return True 
    return False
