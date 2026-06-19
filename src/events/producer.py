"""
Kafka Producer: Simulates real-time POS/IoT events triggering the agent.
"""
import json
import time
import random
from kafka import KafkaProducer

# Connect to local Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC = "supply-chain-events"

print("📡 [PRODUCER] Connected to Kafka. Broadcasting inventory anomalies...")
print("   (Press Ctrl+C to stop)\n")

# Simulate different anomalies happening in real-time
scenarios = [
    {"store_id": 4, "sku": "SKU-100", "current_stock": 3, "reason": "Viral TikTok trend causing massive spike"},
    {"store_id": 7, "sku": "SKU-105", "current_stock": 8, "reason": "Local holiday promotion"},
    {"store_id": 2, "sku": "SKU-103", "current_stock": 2, "reason": "Delivery truck broke down"}
]

try:
    for i, scenario in enumerate(scenarios):
        event = {
            "event_id": f"EVT-{1000+i}",
            "type": "inventory_anomaly",
            "store_id": scenario["store_id"],
            "sku": scenario["sku"],
            "current_stock": scenario["current_stock"],
            "timestamp": time.time(),
            "context": scenario["reason"]
        }
        
        # Send to Kafka
        producer.send(TOPIC, value=event)
        print(f"📤 Broadcasted Anomaly: Store {scenario['store_id']}, {scenario['sku']} - {scenario['reason']}")
        
        # Wait a bit between events to let the consumer process them
        time.sleep(5) 
        
except KeyboardInterrupt:
    print("\n🛑 Producer stopped.")
finally:
    producer.close()