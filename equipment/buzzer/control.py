from equipment.buzzer.hardware import BuzzerHardware
import time

class Buzzer:
    def __init__(self, pin):
        self.hw = BuzzerHardware(pin)

    def beep(self, frequency=1000, duration=200):
        self.hw.set_freq(frequency)
        self.hw.on()
        time.sleep_ms(duration)
        self.hw.off()

    def hum(self, frequency=150, duration=2):
        self.hw.set_freq(frequency)
        self.hw.on()
        time.sleep(duration)
        self.hw.off()

    def alarm(self, cycles=5, tone_duration=200, pause_duration=100):
        for _ in range(cycles):
            self.hw.set_freq(1500)
            self.hw.on(40000)
            time.sleep_ms(tone_duration)
            self.hw.off()
            time.sleep_ms(pause_duration)

            self.hw.set_freq(900)
            self.hw.on(40000)
            time.sleep_ms(tone_duration)
            self.hw.off()
            time.sleep_ms(pause_duration)

    def pulse_burst(self, duration=1000, on_time=30, off_time=30, frequency=300):
        self.hw.set_freq(frequency)
        end_time = time.ticks_ms() + duration
        while time.ticks_ms() < end_time:
            self.hw.on()
            time.sleep_ms(on_time)
            self.hw.off()
            time.sleep_ms(off_time)

    def tick(self):
        self.hw.set_freq(200)
        self.hw.on(40000)
        time.sleep_ms(10)
        self.hw.off()
        time.sleep_ms(20)

    def click(self):
        self.hw.set_freq(1000)
        self.hw.on(30000)
        time.sleep_ms(5)
        self.hw.off()
        time.sleep_ms(20)

    def target_reached(self):
        for freq in (1200, 1800):
            self.hw.set_freq(freq)
            self.hw.on(30000)
            time.sleep_ms(100)
            self.hw.off()
            time.sleep_ms(50)
