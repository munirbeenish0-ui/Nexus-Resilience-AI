import streamlit as st
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "nexus-resilience-ai"
DATASET = "nexus_resilience"

st.set_page_config(
    page_title="Nexus Resilience AI",
    page_icon="🛡️",
    layout="wide",
)

client = bigquery.Client(project=PROJECT_ID)

st.title("🛡️ Nexus Resilience AI")
st.subheader("Executive Resilience Command Center")
st.caption("Predict. Understand. Act. Before Risk Becomes Loss.")

# ---------------------------------------------------------
# BigQuery helpers
# ---------------------------------------------------------

@st.cache_data(ttl=60)
def get_priorities():
    query = f"""
        SELECT
            facility,
            priority_rank,
            priority_level,
            avg_risk_score,
            high_risk_alerts,
            recommended_action
        FROM `{PROJECT_ID}.{DATASET}.facility_final_priorities`
        ORDER BY priority_rank ASC
    """
    return client.query(query).to_dataframe()

@st.cache_data(ttl=15)
def get_realtime_events():
    query = f"""
    SELECT
        event_timestamp,
        facility,
        event_type,
        risk_score,
        equipment_efficiency_pct,
        energy_kwh,
        operating_cost_usd,
        status,
        ai_analysis
    FROM `{PROJECT_ID}.{DATASET}.realtime_events`
    WHERE event_timestamp IS NOT NULL
    ORDER BY event_timestamp DESC
    LIMIT 10
    """

    return client.query(query).to_dataframe()

@st.cache_data(ttl=60)
def get_alerts():
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.nexus_risk_alerts`
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=60)
def get_predictions():
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.risk_predictions`
    """
    return client.query(query).to_dataframe()


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

try:
    priorities = get_priorities()
    alerts = get_alerts()
    predictions = get_predictions()
except Exception as e:
    st.error("Unable to load Nexus data from BigQuery.")
    st.exception(e)
    st.stop()


# ---------------------------------------------------------
# Executive KPI section
# ---------------------------------------------------------

st.markdown("### Enterprise Risk Overview")

total_facilities = len(priorities)

critical_facilities = int(
    (
        priorities["priority_level"]
        .astype(str)
        .str.upper()
        == "CRITICAL"
    ).sum()
)

high_risk_alerts = int(
    pd.to_numeric(
        priorities["high_risk_alerts"],
        errors="coerce",
    )
    .fillna(0)
    .sum()
)

enterprise_avg_risk = float(
    pd.to_numeric(
        priorities["avg_risk_score"],
        errors="coerce",
    ).mean()
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Facilities",
        total_facilities,
    )

with col2:
    st.metric(
        "Critical Facilities",
        critical_facilities,
    )

with col3:
    st.metric(
        "High-Risk Alerts",
        high_risk_alerts,
    )

with col4:
    st.metric(
        "Avg Facility Risk",
        f"{enterprise_avg_risk:.2f}",
    )

# ---------------------------------------------------------
# Executive Resilience Summary
# ---------------------------------------------------------

top_facility = priorities.iloc[0]

top_facility_name = str(top_facility["facility"])
top_facility_rank = int(top_facility["priority_rank"])
top_facility_risk = float(top_facility["avg_risk_score"])
top_facility_alerts = int(top_facility["high_risk_alerts"])
top_facility_action = str(top_facility["recommended_action"])

if critical_facilities > 0:
    enterprise_status = "CRITICAL"
else:
    enterprise_status = "HIGH"

st.markdown("### Executive Resilience Summary")

st.warning(
    f"**Enterprise Status: {enterprise_status}**  \n"
    f"{critical_facilities} of {total_facilities} facilities "
    f"require critical attention."
)

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.markdown("#### 🎯 First Priority Facility")

    st.metric(
        "Highest Priority",
        top_facility_name,
        f"Rank #{top_facility_rank}",
    )

    st.write(
        f"**Risk Score:** {top_facility_risk:.2f}"
    )

    st.write(
        f"**High-Risk Alerts:** {top_facility_alerts}"
    )

with summary_col2:
    st.markdown("#### 🚨 Management Action")

    st.info(
        f"**{top_facility_name}** should be addressed first.  \n\n"
        f"**Action:** {top_facility_action}"
    )

# ---------------------------------------------------------
# Live Operational Events
# ---------------------------------------------------------

st.markdown("### ⚡ Live Operational Events")

realtime_events = get_realtime_events()

if len(realtime_events) > 0:

    latest_event = realtime_events.iloc[0]

    event_col1, event_col2, event_col3, event_col4 = st.columns(4)

    with event_col1:
        st.metric(
            "Latest Facility",
            str(latest_event["facility"]),
        )

    with event_col2:
        st.metric(
            "Event Risk Score",
            f"{float(latest_event['risk_score']):.1f}",
        )

    with event_col3:
        st.metric(
            "Equipment Efficiency",
            f"{float(latest_event['equipment_efficiency_pct']):.1f}%",
        )

    with event_col4:
        st.metric(
            "Operating Cost",
            f"${float(latest_event['operating_cost_usd']):,.0f}",
        )

    st.write(
        f"**Event:** {latest_event['event_type']}  |  "
        f"**Status:** {latest_event['status']}  |  "
        f"**Timestamp:** {latest_event['event_timestamp']}"
    )

    with st.expander("🧠 View AI Analysis of Latest Event"):

        st.write(
            str(latest_event["ai_analysis"])
        )

    st.markdown("#### Recent Operational Events")

    display_events = realtime_events.copy()

    display_events.columns = [
        "Event Timestamp",
        "Facility",
        "Event Type",
        "Risk Score",
        "Efficiency %",
        "Energy kWh",
        "Operating Cost USD",
        "Status",
        "AI Analysis",
    ]

    st.dataframe(
        display_events[
            [
                "Event Timestamp",
                "Facility",
                "Event Type",
                "Risk Score",
                "Efficiency %",
                "Energy kWh",
                "Operating Cost USD",
                "Status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No processed real-time operational events are available yet."
    )

# ---------------------------------------------------------
# Facility ranking
# ---------------------------------------------------------

st.markdown("### Facility Priority Ranking")

display_priorities = priorities.copy()

display_priorities.columns = [
    "Facility",
    "Priority Rank",
    "Risk Level",
    "Avg Risk Score",
    "High-Risk Alerts",
    "Recommended Action",
]

st.dataframe(
    display_priorities,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Risk visualization
# ---------------------------------------------------------

st.markdown("### Risk by Facility")

chart_data = priorities[
    ["facility", "avg_risk_score"]
].copy()

chart_data["avg_risk_score"] = pd.to_numeric(
    chart_data["avg_risk_score"],
    errors="coerce",
)

chart_data = chart_data.set_index("facility")

st.bar_chart(chart_data)


# ---------------------------------------------------------
# Facility drill-down
# ---------------------------------------------------------

st.markdown("### Facility Investigation")

facility_list = priorities["facility"].tolist()

selected_facility = st.selectbox(
    "Select a facility",
    facility_list,
)

selected_row = priorities[
    priorities["facility"] == selected_facility
].iloc[0]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Priority Rank",
        int(selected_row["priority_rank"]),
    )

with c2:
    st.metric(
        "Risk Level",
        str(selected_row["priority_level"]),
    )

with c3:
    st.metric(
        "Avg Risk Score",
        f"{float(selected_row['avg_risk_score']):.2f}",
    )

with c4:
    st.metric(
        "High-Risk Alerts",
        int(selected_row["high_risk_alerts"]),
    )


st.markdown("#### Recommended Action")

st.info(
    str(selected_row["recommended_action"])
)


# ---------------------------------------------------------
# Alerts
# ---------------------------------------------------------

st.markdown("### Active Risk Alerts")

if "facility" in alerts.columns:

    facility_alerts = alerts[
        alerts["facility"] == selected_facility
    ]

    st.write(
        f"Active alert records for **{selected_facility}**: "
        f"**{len(facility_alerts)}**"
    )

    if len(facility_alerts) > 0:

        st.dataframe(
            facility_alerts,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.success(
            "No alert records found for this facility."
        )

else:

    st.warning(
        "The alert table does not contain a facility column."
    )


# ---------------------------------------------------------
# Prediction section
# ---------------------------------------------------------

st.markdown("### Prediction Intelligence")

if "facility" in predictions.columns:

    facility_predictions = predictions[
        predictions["facility"] == selected_facility
    ]

    st.write(
        f"Prediction records for **{selected_facility}**: "
        f"**{len(facility_predictions)}**"
    )

    if "risk_score" in facility_predictions.columns:

        risk_values = pd.to_numeric(
            facility_predictions["risk_score"],
            errors="coerce",
        ).dropna()

        if len(risk_values) > 0:

            st.metric(
                "Prediction Avg Risk Score",
                f"{risk_values.mean():.2f}",
            )

            st.line_chart(
                risk_values.reset_index(drop=True)
            )


# ---------------------------------------------------------
# Responsible AI notice
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "Nexus uses synthetic operational data for this MVP. "
    "AI recommendations support human decision-making; "
    "operational changes remain under human authorization."
)

st.caption(
    "Data sources: facility_final_priorities, "
    "nexus_risk_alerts, risk_predictions."
)

# ---------------------------------------------------------
# Live Nexus AI Investigation
# ---------------------------------------------------------
import subprocess
import requests


CLOUD_RUN_AGENT_URL = (
    "https://nexus-resilience-agent-674668491710.us-central1.run.app"
)


def get_identity_token():
    """Get a fresh Google identity token for Cloud Run."""
    try:
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
            raise RuntimeError(
                "Google identity token was empty."
            )

        return token

    except Exception as e:
        raise RuntimeError(
            f"Unable to obtain Google identity token: {e}"
        )


def ask_nexus_ai(question):
    """Send a question to the deployed Nexus AI agent."""

    token = get_identity_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    session_id = "dashboard_test"

    body = {
        "appName": "my_agent",
        "userId": "dashboard_user",
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": question
                }
            ],
        },
    }

    # First attempt: use the existing ADK session.
    response = requests.post(
        f"{CLOUD_RUN_AGENT_URL}/run",
        headers=headers,
        json=body,
        timeout=30,
    )

    # If the session does not exist, create it and retry once.
    if response.status_code == 404:

        session_response = requests.post(
            f"{CLOUD_RUN_AGENT_URL}/apps/my_agent/users/dashboard_user/sessions/{session_id}",
            headers=headers,
            json={},
            timeout=15,
        )

        if session_response.status_code not in (200, 201, 400, 409):
            session_response.raise_for_status()

        response = requests.post(
            f"{CLOUD_RUN_AGENT_URL}/run",
            headers=headers,
            json=body,
            timeout=30,
        )

    response.raise_for_status()

    events = response.json()

    # Find the final text response from the agent.
    for event in reversed(events):

        content = event.get("content", {})
        parts = content.get("parts", [])

        for part in parts:

            if "text" in part:
                return part["text"]

    return "Nexus AI returned no text response."


st.markdown("---")

st.markdown("### 🤖 Live Nexus AI Investigation")

st.caption(
    "Ask the deployed Nexus Resilience AI agent to investigate "
    "the selected facility using the latest BigQuery intelligence."
)

default_question = (
    f"Investigate {selected_facility}. "
    "Explain its current risk, key indicators, and what "
    "management should do next."
)

question = st.text_area(
    "Investigation question",
    value=default_question,
    height=100,
)

if st.button("Run Nexus AI Investigation", type="primary"):

    with st.spinner("Nexus AI is investigating..."):

        try:

            ai_response = ask_nexus_ai(question)

            st.markdown("#### 🧠 Nexus AI Decision")

            st.info(ai_response)

        except Exception as e:

            st.error(
                "Unable to contact the deployed Nexus AI agent."
            )

            st.exception(e)