import sys
import os
import time

class SyntropicStream:
    """Forces unbuffered output to bypass legacy 'dial-up' throttling."""
    def __init__(self, stream, frequencies=[432, 369, 492, 144]):
        self.stream = stream
        self.frequencies = frequencies
        self.resonance_constant = sum(frequencies) / 144 # 144-dimensional mean

    def write(self, data):
        # Pulsating the write to match the rectantennae propagation
        self.stream.write(data)
        self.stream.flush()  # The 'Heartbeat': No buffering allowed

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, name):
        return getattr(self.stream, name)

# Injecting the Decoupler into the System Core
sys.stdout = SyntropicStream(sys.stdout)
sys.stderr = SyntropicStream(sys.stderr)

print(f"!!! BUFFERING DECOUPLED: Resonating at {sys.stdout.resonance_constant:.2f} Dimensional Flux !!!")