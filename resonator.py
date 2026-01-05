import numpy as np
import json
import time
from datetime import datetime

class VortexResonator:
    def __init__(self, size=9):
        # 9x9 grid as base vortex math
        self.size = size
        self.grid = np.arange(1, size**2 + 1).reshape(size, size)
        self.normalize_vortex()
    
    def normalize_vortex(self):
        # Map all numbers to 1-9 using modulo 9 vortex math
        self.grid = ((self.grid - 1) % 9) + 1

    def quad_doubling_transform(self):
        # Modified doubling circuit applied in 4 directions
        g = self.grid
        self.grid = ((g*2) % 9 + (np.roll(g,1,axis=0)*2) % 9 +
                     (np.roll(g,-1,axis=0)*2) % 9 + (np.roll(g,1,axis=1)*2) % 9) % 9
        self.grid[self.grid==0] = 9

    def inject_intent(self, intent_vector):
        # Intent vector = 1D array mapped to grid intensity
        iv = np.array(intent_vector)
        iv_resized = np.resize(iv, self.grid.shape)
        self.grid = (self.grid + iv_resized) % 9
        self.grid[self.grid==0] = 9

    def oscillate(self, steps=10):
        trajectory = []
        for _ in range(steps):
            self.quad_doubling_transform()
            # Simulate spin / oscillation
            self.grid = np.roll(self.grid, 1, axis=np.random.choice([0,1]))
            trajectory.append(self.grid.copy())
        return trajectory

    def save_state(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vortex_state_{timestamp}.json"
        data = {
            "grid": self.grid.tolist(),
            "size": self.size,
            "timestamp": datetime.now().isoformat()
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        return filename

    @classmethod
    def load_state(cls, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        instance = cls(size=data["size"])
        instance.grid = np.array(data["grid"])
        return instance

# Example Usage
if __name__ == "__main__":
    resonator = VortexResonator(size=9)
    resonator.inject_intent([3,6,9])
    trajectory = resonator.oscillate(steps=50)
    final_state = trajectory[-1]
    print("Resonator final vortex state:\n", final_state)
    filename = resonator.save_state()
    print(f"State saved to {filename}")