from machine import PWM, Pin
import time

class Buzzer:
    def __init__(self, pin):
        self.pwm = PWM(pin)

    def beep(self, frequency=1000, duration=200):
        self.pwm.freq(frequency)
        self.pwm.duty_u16(32768)  # 50% duty
        time.sleep_ms(duration)
        self.pwm.duty_u16(0)

    def hum(self, frequency=150, duration=2):
        self.pwm.freq(frequency)
        self.pwm.duty_u16(32768)
        time.sleep(duration)
        self.pwm.duty_u16(0)
        
    def alarm(self, cycles=5, tone_duration=200, pause_duration=100):
        """
        Simulates a nuclear alarm:
        Alternating high/low frequency pulses in repeating cycles.
        """
        for _ in range(cycles):
            # High tone
            self.pwm.freq(1500)
            self.pwm.duty_u16(40000)
            time.sleep_ms(tone_duration)
            self.pwm.duty_u16(0)
            time.sleep_ms(pause_duration)

            # Low tone
            self.pwm.freq(900)
            self.pwm.duty_u16(40000)
            time.sleep_ms(tone_duration)
            self.pwm.duty_u16(0)
            time.sleep_ms(pause_duration)

                
    def pulse_burst(self, duration=1000, on_time=30, off_time=30, frequency=300):
        self.pwm.freq(frequency)
        end_time = time.ticks_ms() + duration
        while time.ticks_ms() < end_time:
            self.pwm.duty_u16(32768)
            time.sleep_ms(on_time)
            self.pwm.duty_u16(0)
            time.sleep_ms(off_time)

    def tick(self):
        self.pwm.freq(200)
        self.pwm.duty_u16(40000)
        time.sleep_ms(10)
        self.pwm.duty_u16(0)
        time.sleep_ms(20)

    def click(self):
        self.pwm.freq(1000)
        self.pwm.duty_u16(30000)
        time.sleep_ms(5)
        self.pwm.duty_u16(0)
        time.sleep_ms(20)
        
    def target_reached(self):
        """Plays a short double tone to indicate target reached."""
        for freq in (1200, 1800):
            self.pwm.freq(freq)
            self.pwm.duty_u16(30000)
            time.sleep_ms(100)
            self.pwm.duty_u16(0)
            time.sleep_ms(50)


def test():
    buzzer = Buzzer(Pin(16))
    buzzer.alarm()
    raise ""
    buzzer.beep()
    time.sleep(1)
    buzzer.hum()
    time.sleep(1)
    buzzer.click()
    time.sleep(1)
    buzzer.pulse_burst()
    time.sleep(1)
    buzzer.tick()
    time.sleep(1)

if __name__ == "__main__":
    test()
