import datetime
import json
import subprocess
import requests

from google.cloud import pubsub_v1
from google.cloud import bigquery


PROJECT_ID = "nexus-resilience-ai"
DATASET_ID = "nexus_resilience"
TABLE_ID = "realtime_events"

SUBSCRIPTION_ID = "nexus-operational-events-sub"

CLOUD_RUN_AGENT_URL = (
    "https://nexus-resilience-agent-674668491710.us-central1.run.app"
)

FACILITY_USER = "realtime_processor"
SESSION_ID = "realtime_event_session"


def get_identity_token():
    """Get a fresh Google identity token for Cloud Run."""

    result = subprocess.run(
        [
            r"C:\Users\RTC\google-cloud-sdk\bin\gcloud.cmd",
            "auth",
            "print-identity-token",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    token = result.stdout.strip()

    if not token:
        raise RuntimeError("Google identity token was empty.")

    return token


def create_session(token):
    """Create the ADK session used by the realtime processor."""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = (
        f"{CLOUD_RUN_AGENT_URL}/apps/my_agent/"
        f"users/{FACILITY_USER}/sessions/{SESSION_ID}"
    )

    response = requests.post(
        url,
        headers=headers,
        json={},
        timeout=15,
    )

    if response.status_code not in (200, 201, 400, 409):
        response.raise_for_status()


def analyze_event(event):
    """Send a realtime operational event to Nexus AI."""

    token = get_identity_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    question = (
        "A new real-time operational event has been detected.\n\n"
        f"{json.dumps(event, indent=2)}\n\n"
        "Assess the event for operational risk. "
        "Identify the facility, explain the significance of the "
        "reported indicators, and state what management should "
        "consider doing next. Use authoritative facility priority "
        "data when relevant. Do not invent facts."
    )

    body = {
        "appName": "my_agent",
        "userId": FACILITY_USER,
        "sessionId": SESSION_ID,
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": question
                }
            ],
        },
    }

    response = requests.post(
        f"{CLOUD_RUN_AGENT_URL}/run",
        headers=headers,
        json=body,
        timeout=60,
    )

    if response.status_code == 404:
        create_session(token)

        response = requests.post(
            f"{CLOUD_RUN_AGENT_URL}/run",
            headers=headers,
            json=body,
            timeout=60,
        )

    response.raise_for_status()

    events = response.json()

    for event_item in reversed(events):

        content = event_item.get("content", {})
        parts = content.get("parts", [])

        for part in parts:

            if "text" in part:
                return part["text"]

    return "Nexus AI returned no text response."


def save_realtime_event(event, analysis):
    """Save the successfully analyzed event to BigQuery."""

    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    schema = [
        bigquery.SchemaField("event_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("facility", "STRING"),
        bigquery.SchemaField("event_type", "STRING"),
        bigquery.SchemaField("risk_score", "FLOAT"),
        bigquery.SchemaField("energy_kwh", "FLOAT"),
        bigquery.SchemaField("equipment_efficiency_pct", "FLOAT"),
        bigquery.SchemaField("operating_cost_usd", "FLOAT"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("ai_analysis", "STRING"),
    ]

    try:
        client.get_table(table_ref)

    except Exception:

        table = bigquery.Table(table_ref, schema=schema)

        client.create_table(table)

        print("")
        print("Created BigQuery table:")
        print(table_ref)

    row = {
        "event_timestamp": bigquery.ScalarQueryParameter(
            "event_timestamp",
            "TIMESTAMP",
            None,
        )
    }

    rows_to_insert = [
        {
            "event_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "facility": event.get("facility"),
            "event_type": event.get("event_type"),
            "risk_score": event.get("risk_score"),
            "energy_kwh": event.get("energy_kwh"),
            "equipment_efficiency_pct": event.get(
                "equipment_efficiency_pct"
            ),
            "operating_cost_usd": event.get(
                "operating_cost_usd"
            ),
            "status": event.get("status"),
            "ai_analysis": analysis,
        }
    ]

    errors = client.insert_rows_json(
        table_ref,
        rows_to_insert,
    )

    if errors:
        raise RuntimeError(
            f"BigQuery insert failed: {errors}"
        )

    print("")
    print("REAL-TIME EVENT SAVED TO BIGQUERY")
    print("----------------------------------------")
    print(table_ref)


def process_event(event_json):
    """Process one Pub/Sub operational event."""

    event = json.loads(event_json)

    print("")
    print("========================================")
    print("NEXUS REAL-TIME EVENT")
    print("========================================")

    print(f"Facility: {event.get('facility')}")
    print(f"Event Type: {event.get('event_type')}")
    print(f"Risk Score: {event.get('risk_score')}")
    print(
        f"Efficiency: "
        f"{event.get('equipment_efficiency_pct')}%"
    )
    print(f"Energy: {event.get('energy_kwh')} kWh")
    print(
        f"Operating Cost: "
        f"${event.get('operating_cost_usd')}"
    )
    print(f"Status: {event.get('status')}")

    print("")
    print("NEXUS AI ANALYSIS")
    print("----------------------------------------")

    analysis = analyze_event(event)

    print(analysis)

    save_realtime_event(event, analysis)

    print("========================================")
    print("EVENT PROCESSING COMPLETE")
    print("========================================")
    print("")


def callback(message):
    """Handle messages received from Pub/Sub."""

    try:
        print("")
        print(">>> NEW PUB/SUB MESSAGE RECEIVED <<<")

        event_json = message.data.decode("utf-8")

        process_event(event_json)

        # Acknowledge only after successful AI
        # processing AND BigQuery storage.
        message.ack()

        print(">>> PUB/SUB MESSAGE ACKNOWLEDGED <<<")

    except Exception as e:

        print("")
        print("!!! ERROR PROCESSING PUB/SUB MESSAGE !!!")
        print(str(e))
        print("Message will remain available for retry.")

        message.nack()


def main():
    """Start the Nexus real-time Pub/Sub listener."""

    subscriber = pubsub_v1.SubscriberClient()

    subscription_path = subscriber.subscription_path(
        PROJECT_ID,
        SUBSCRIPTION_ID,
    )

    print("========================================")
    print("NEXUS REAL-TIME PROCESSOR")
    print("========================================")
    print(f"Project: {PROJECT_ID}")
    print(f"Subscription: {SUBSCRIPTION_ID}")
    print("")
    print("Waiting for operational events...")
    print("Press Ctrl+C to stop.")
    print("========================================")

    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=callback,
    )

    try:
        streaming_pull_future.result()

    except KeyboardInterrupt:

        print("")
        print("Stopping Nexus real-time processor...")

        streaming_pull_future.cancel()
        streaming_pull_future.result()

    finally:
        subscriber.close()


if __name__ == "__main__":
    main()