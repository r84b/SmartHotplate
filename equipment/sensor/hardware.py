from machine import ADC
import math

class PT1000Sensor:
    def __init__(self, adc_pin, v_ref=3.3, r_ref=967, alpha=0.003851, debug=False):
        self.adc = ADC(adc_pin)
        self.v_ref = v_ref
        self.r_ref = r_ref
        self.R0 = 1000.0
        self.alpha = alpha
        self.debug = debug
        self.history = []
        self.current_temp = None

    def _median_of_group_means(self, samples, group_size=16):
        groups = [samples[i:i + group_size] for i in range(0, len(samples), group_size)]
        means = [sum(g) / len(g) for g in groups if g]
        sorted_means = sorted(means)
        n = len(sorted_means)
        m = n // 2
        return sorted_means[m] if n % 2 == 1 else (sorted_means[m - 1] + sorted_means[m]) / 2

    def read_voltage(self):
        _ = [self.adc.read_u16() for _ in range(5)]  # discard initial noise
        raw_values = [self.adc.read_u16() for _ in range(128)]
        avg = self._median_of_group_means(raw_values, group_size=16)
        v = (avg / 65535) * self.v_ref
        if self.debug:
            print(f"[DEBUG] median ADC: {avg:.1f} → V: {v:.4f} V")
        return v

    def read_resistance(self):
        v_out = self.read_voltage()
        if not (0.01 < v_out < self.v_ref - 0.01):
            return None
        r = self.r_ref * v_out / (self.v_ref - v_out)
        if self.debug:
            print(f"[DEBUG] R_pt1000: {r:.2f} Ω")
        return r

    def read_temperature(self):
        r = self.read_resistance()
        if r is None:
            return None
        temp = (r - self.R0) / (self.R0 * self.alpha)
        if self.debug:
            print(f"[DEBUG] Temp: {temp:.2f} °C")
        return temp

    def update(self):
        sample = self.read_temperature()
        if sample is None:
            self.current_temp = None
            return None
        self.history.append(sample)
        if len(self.history) > 5:
            self.history.pop(0)
        self.current_temp = round(sum(self.history) / len(self.history), 1)
