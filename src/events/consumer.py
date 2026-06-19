"""
Kafka Consumer: Listens for anomalies and automatically triggers the LangGraph Agent.
"""
import json
import sys
import os

# Add parent directory to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kafka import KafkaConsumer
from src.main import run_agent

TOPIC = "supply-chain-events"

print("👂 [CONSUMER] Listening to Kafka topic 'supply-chain-events'...")
print("   Waiting for anomalies to wake up the agent...\n")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='supply-chain-agent-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

try:
    for message in consumer:
        event = message.value
        
        if event.get('type') == 'inventory_anomaly':
            print("\n" + "="*80)
            print(f"🚨 ANOMALY DETECTED VIA KAFKA!")
            print(f"   Event ID: {event['event_id']}")
            print(f"   Store: {event['store_id']}")
            print(f"   SKU: {event['sku']}")
            print(f"   Context: {event.get('context', 'Unknown')}")
            print("="*80 + "\n")
            
            # 🚀 AUTOMATICALLY TRIGGER THE LANGGRAPH AGENT
            alert_message = f"Kafka Alert: {event.get('context', 'Stock anomaly detected')}. Current stock is {event['current_stock']}."
            
            run_agent(
                store_id=event['store_id'],
                sku=event['sku'],
                alert=alert_message
            )
            
            print("\n✅ Agent finished processing this event. Resuming Kafka listener...\n")

except KeyboardInterrupt:
    print("\n🛑 Consumer stopped.")
finally:
    consumer.close()