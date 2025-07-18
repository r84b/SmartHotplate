class TakahashiPID:
    def __init__(self, Kc, Ti, Td, output_limits=(0.0, 1.0)):
        # Takahashi tuningregels
        self.Kc = Kc
        self.Ti = Ti
        self.Td = Td

        self.integral = 0
        self.prev_error = 0

        self.output_min, self.output_max = output_limits

    def compute(self, setpoint, measurement, dt):
        error = setpoint - measurement
        
        if abs(error) < 1.0:
            error = 0.0

        # Proportioneel
        P = self.Kc * error

        # Integraal
        #print(f"Kc: {self.Kc}, Error: {error}, P: {P}")
        self.integral += error * dt
        #print(f"integral: {self.integral} = error: {error} * dt: {dt}")
        I = self.Kc / self.Ti * self.integral
        #print(f"I: {I}, Kc: {self.Kc}, Ti: {self.Ti}, integral: {self.integral}")
    
        # Afgeleide
        D = self.Kc * self.Td * (error - self.prev_error) / dt

        output = P + I + D
        #print(output)
        #output = max(self.output_min, min(self.output_max, output))
        
        #print(measurement, setpoint, P, I, D, output)

        self.prev_error = error

        return output