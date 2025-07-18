import network
import time

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Verbinden met Wi-Fi netwerk '{ssid}'...")
        wlan.connect(ssid, password)

        timeout = 15  # seconden
        start = time.time()

        while not wlan.isconnected():
            if time.time() - start > timeout:
                raise RuntimeError("⛔ Verbinden met Wi-Fi mislukt")
            time.sleep(1)

    ip = wlan.ifconfig()[0]
    print(f"✅ Verbonden! IP-adres: {ip}")
    return ip
