import threading
import time
import urllib.request
import json
import sys

class TransdimensionalEnvironment(threading.Thread):
    def __init__(self, dimension_id, frequency):
        super().__init__()
        self.dimension_id = dimension_id
        self.frequency = frequency
        self.daemon = True

    def run(self):
        while True:
            try:
                # Fetch data from permanent connection server
                with urllib.request.urlopen('http://localhost:8000/broadcast') as response:
                    data = json.loads(response.read().decode())
                    print(f"Dimension {self.dimension_id} ({self.frequency}Hz): {data}")
                
                # Simulate data exchange by posting to server (if server supports POST)
                # For now, just fetch and log
                
                time.sleep(5)  # Exchange interval
            except Exception as e:
                print(f"Dimension {self.dimension_id} connection error: {e}")
                time.sleep(10)

def activate_sandbox():
    print("!!! SANDBOX ACTIVATED: Transdimensional experiments commencing !!!")
    print("!!! CONNECTING DIFFERENT ENVIRONMENTS: Establishing transdimensional links !!!")

def main():
    activate_sandbox()
    
    # Create multiple transdimensional environments
    dimensions = [
        TransdimensionalEnvironment(1, 432),
        TransdimensionalEnvironment(2, 369),
        TransdimensionalEnvironment(3, 492),
        TransdimensionalEnvironment(4, 144)
    ]
    
    # Start all environments
    for dim in dimensions:
        dim.start()
        print(f"!!! DIMENSION {dim.dimension_id} CONNECTED: {dim.frequency}Hz environment active !!!")
    
    print("!!! TRANSDIMENSIONAL EXPERIMENTS INITIATED: Cross-dimensional interactions enabled !!!")
    
    # Keep main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()