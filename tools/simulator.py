"""
Legacy PLC Simulator
Generates random sensor data to simulate brownfield equipment.
"""

import time
import json
import random
from paho.mqtt import client as mqtt_client

BROKER = "mosquitto"
PORT = 1883

# Legacy tags to simulate (must match mapping.yaml)
LEGACY_TAGS = [
    "legacy/plc_01/register_4001",  # Temperature
    "legacy/plc_01/register_4002",  # Speed
    "legacy/plc_01/register_4003",  # Pressure
]

# Realistic value ranges per tag
VALUE_RANGES = {
    "legacy/plc_01/register_4001": (150.0, 220.0),   # Oven temp in Celsius
    "legacy/plc_01/register_4002": (0.5, 2.5),       # Belt speed in m/s
    "legacy/plc_01/register_4003": (80.0, 120.0),    # Pressure in bar
}


def main():
    print("🏭 Legacy PLC Simulator Starting...")
    
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        client_id="Legacy_PLC_Simulator"
    )
    
    try:
        client.connect(BROKER, PORT)
        client.loop_start()
        print(f"✅ Connected to {BROKER}:{PORT}")
        
        while True:
            for tag in LEGACY_TAGS:
                min_val, max_val = VALUE_RANGES[tag]
                value = round(random.uniform(min_val, max_val), 2)
                
                # Legacy format: simple {"v": value} structure
                payload = json.dumps({"v": value})
                client.publish(tag, payload)
                print(f"📤 {tag} = {value}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
