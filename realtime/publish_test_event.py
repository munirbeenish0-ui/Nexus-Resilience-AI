import json
from google.cloud import pubsub_v1

PROJECT_ID = "nexus-resilience-ai"
TOPIC_ID = "nexus-operational-events"

event = {
    "facility": "Facility_D",
    "event_type": "equipment_degradation",
    "risk_score": 99.4,
    "energy_kwh": 22800,
    "equipment_efficiency_pct": 61.8,
    "operating_cost_usd": 21450,
    "status": "Nexus Alert"
}

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

data = json.dumps(event).encode("utf-8")
future = publisher.publish(topic_path, data)

print("Published message ID:", future.result())