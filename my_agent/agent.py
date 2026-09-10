from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.cloud import bigquery
from datetime import date, datetime

PROJECT_ID = "nexus-resilience-ai"
DATASET = "nexus_resilience"

client = bigquery.Client(project=PROJECT_ID)


def get_facility_priorities() -> list[dict]:
    """Return the authoritative current priority ranking for all facilities."""

    query = f"""
    SELECT
        facility,
        priority_rank,
        priority_level,
        high_risk_alerts,
        avg_risk_score,
        avg_efficiency_pct,
        avg_operating_cost_usd,
        recommended_action
    FROM `{PROJECT_ID}.{DATASET}.facility_final_priorities`
    ORDER BY priority_rank
    """

    rows = client.query(query).result()

    results = []


    for row in rows:
        record = dict(row)

        for key, value in record.items():
            if isinstance(value, (date, datetime)):
                record[key] = value.isoformat()

        results.append(record)

    return results


def compare_facilities(facility_a: str, facility_b: str) -> list[dict]:
    """Compare two facilities using authoritative priority data."""

    query = f"""
    SELECT
        facility,
        priority_rank,
        priority_level,
        high_risk_alerts,
        avg_risk_score,
        avg_efficiency_pct,
        avg_operating_cost_usd,
        recommended_action
    FROM `{PROJECT_ID}.{DATASET}.facility_final_priorities`
    WHERE facility IN (@facility_a, @facility_b)
    ORDER BY priority_rank
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("facility_a", "STRING", facility_a),
            bigquery.ScalarQueryParameter("facility_b", "STRING", facility_b),
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return [dict(row) for row in rows]


def get_facility_health(facility: str) -> dict:
    """Return an executive health assessment for one facility."""

    priority = get_facility_priorities()
    priority_record = next(
        (row for row in priority if row["facility"] == facility),
        None,
    )

    if priority_record is None:
        return {
            "facility": facility,
            "error": "Facility not found in facility_final_priorities.",
        }

    alerts = get_facility_alerts(facility)
    top_risks = get_top_risks(facility)
    disagreements = analyze_prediction_disagreements(facility)

    return {
        "facility": facility,
        "priority": priority_record,
        "active_alerts": alerts,
        "top_risk_predictions": top_risks,
        "prediction_disagreements": disagreements,
    }

def get_all_facilities_health() -> list[dict]:
    """Return a compact executive health summary for all facilities."""

    priorities = get_facility_priorities()

    # Get alert counts for all facilities in one query.
    alert_query = f"""
    SELECT
        facility,
        risk_level,
        COUNT(*) AS alert_count
    FROM `{PROJECT_ID}.{DATASET}.nexus_risk_alerts`
    WHERE risk_level IN ('HIGH', 'MEDIUM')
      AND nexus_status = 'Nexus Alert'
    GROUP BY facility, risk_level
    ORDER BY facility, risk_level
    """

    alert_rows = client.query(alert_query).result()

    alerts_by_facility = {}

    for row in alert_rows:
        facility = row["facility"]

        if facility not in alerts_by_facility:
            alerts_by_facility[facility] = []

        alerts_by_facility[facility].append({
            "facility": row["facility"],
            "risk_level": row["risk_level"],
            "alert_count": row["alert_count"],
        })

    # Get prediction disagreement statistics for all facilities
    # in one query.
    disagreement_query = f"""
    WITH predictions AS (
        SELECT
            facility,
            risk_score,
            predicted_risk_event,
            (
                SELECT p.prob
                FROM UNNEST(predicted_risk_event_probs) AS p
                WHERE p.label = 1
                LIMIT 1
            ) AS probability_event_1
        FROM `{PROJECT_ID}.{DATASET}.risk_predictions`
    )

    SELECT
        facility,
        COUNT(*) AS total_records,
        COUNTIF(
            predicted_risk_event = 0
            AND probability_event_1 >= 0.50
        ) AS disagreement_count,
        SAFE_DIVIDE(
            COUNTIF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50
            ),
            COUNT(*)
        ) AS disagreement_percentage,
        AVG(
            IF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50,
                probability_event_1,
                NULL
            )
        ) AS avg_probability_event_1,
        MAX(
            IF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50,
                probability_event_1,
                NULL
            )
        ) AS max_probability_event_1,
        AVG(
            IF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50,
                risk_score,
                NULL
            )
        ) AS avg_risk_score
    FROM predictions
    GROUP BY facility
    """

    disagreement_rows = client.query(disagreement_query).result()

    disagreements_by_facility = {
        row["facility"]: dict(row)
        for row in disagreement_rows
    }

    # Combine the authoritative priorities with the diagnostics.
    results = []

    for priority in priorities:
        facility = priority["facility"]

        results.append({
            "facility": facility,
            "priority_rank": priority["priority_rank"],
            "priority_level": priority["priority_level"],
            "high_risk_alerts": priority["high_risk_alerts"],
            "avg_risk_score": priority["avg_risk_score"],
            "avg_efficiency_pct": priority["avg_efficiency_pct"],
            "avg_operating_cost_usd": priority["avg_operating_cost_usd"],
            "recommended_action": priority["recommended_action"],
            "active_alerts": alerts_by_facility.get(facility, []),
            "prediction_disagreements": disagreements_by_facility.get(
                facility,
                {}
            ),
        })

    return results


def get_facility_alerts(facility: str) -> list[dict]:
    """Return active HIGH and MEDIUM alert counts for a facility."""

    query = f"""
    SELECT
        facility,
        risk_level,
        COUNT(*) AS alert_count
    FROM `{PROJECT_ID}.{DATASET}.nexus_risk_alerts`
    WHERE facility = @facility
      AND risk_level IN ('HIGH', 'MEDIUM')
      AND nexus_status = 'Nexus Alert'
    GROUP BY facility, risk_level
    ORDER BY risk_level
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("facility", "STRING", facility)
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return [dict(row) for row in rows]

def get_top_risks(facility: str) -> list[dict]:
    """Return the highest-probability risk predictions for a facility."""

    query = f"""
    SELECT
        record_id,
        facility,
        CAST(date AS STRING) AS date,
        scenario,
        risk_score,
        predicted_risk_event,
        predicted_risk_probability,
        (
            SELECT p.prob
            FROM UNNEST(predicted_risk_event_probs) AS p
            WHERE p.label = 1
            LIMIT 1
        ) AS probability_event_1
    FROM `{PROJECT_ID}.{DATASET}.risk_predictions`
    WHERE facility = @facility
    ORDER BY probability_event_1 DESC, risk_score DESC
    LIMIT 10
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("facility", "STRING", facility)
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return [dict(row) for row in rows]

def analyze_prediction_disagreements(facility: str) -> dict:
    """Analyze cases where predicted event is 0 but P(event=1) >= 0.50."""

    query = f"""
    WITH predictions AS (
        SELECT
            record_id,
            facility,
            risk_score,
            predicted_risk_event,
            (
                SELECT p.prob
                FROM UNNEST(predicted_risk_event_probs) AS p
                WHERE p.label = 1
                LIMIT 1
            ) AS probability_event_1
        FROM `{PROJECT_ID}.{DATASET}.risk_predictions`
        WHERE facility = @facility
    )

    SELECT
        COUNT(*) AS total_records,
        COUNTIF(
            predicted_risk_event = 0
            AND probability_event_1 >= 0.50
        ) AS disagreement_count,
        SAFE_DIVIDE(
            COUNTIF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50
            ),
            COUNT(*)
        ) AS disagreement_percentage,
        AVG(
            IF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50,
                probability_event_1,
                NULL
            )
        ) AS avg_probability_event_1,
        MAX(
            IF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50,
                probability_event_1,
                NULL
            )
        ) AS max_probability_event_1,
        AVG(
            IF(
                predicted_risk_event = 0
                AND probability_event_1 >= 0.50,
                risk_score,
                NULL
            )
        ) AS avg_risk_score
    FROM predictions
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("facility", "STRING", facility)
        ]
    )

    row = list(client.query(query, job_config=job_config).result())[0]

    return dict(row)


root_agent = Agent(
    model="gemini-2.5-flash",
    name="nexus_resilience_agent",
    description=(
        "Nexus Resilience analytics agent for facility risk, "
        "alerts, priorities, and prediction diagnostics."
    ),
    instruction="""
You are the Nexus Resilience analytics agent.

Use the provided BigQuery tools to answer questions about facility
risk, priorities, alerts, predictions, and prediction disagreements.

Important rules:

1. Use facility_final_priorities as the authoritative source for
   current facility priority ranking and recommended actions.

2. Use nexus_risk_alerts for active HIGH and MEDIUM risk alerts.

3. Use risk_predictions for individual risk predictions.

4. Calculate P(event=1) directly from predicted_risk_event_probs
   where label = 1.

5. Do not assume predicted_risk_probability means P(event=1).
   It represents the probability of the predicted class.

6. Do not call risk_level a scenario.

7. Clearly distinguish stored database values from calculated values.

8. Do not invent operational causes or recommended actions.
   If the data does not establish something, say so.

9. When reporting a disagreement, define it as:
   predicted_risk_event = 0 AND P(event=1) >= 0.50.

10. When evidence comes from multiple tables, identify which table
    supplied the evidence.

11. Do not compare or combine avg_risk_score from facility_final_priorities
    with risk_score from risk_predictions as though they are the same metric.
    Report each metric with its source table and preserve the metric's meaning.

12. Do not infer or describe how priority_level or priority_rank was calculated
    unless the underlying data or documented logic explicitly establishes it.
    Report the stored priority_level, priority_rank, and related metrics as
    authoritative database values.

    When comparing facilities, you may report that one facility has a higher
    or lower metric than another, but do not state or imply that a metric
    caused, determined, explains, or is associated with the priority rank
    unless the underlying documented logic explicitly establishes that relationship.

13. For executive summaries, organize the response in this order:
    overall assessment, facility ranking, key risk diagnostics, and
    recommended actions supported by the authoritative data.

14. Do not calculate or report totals, percentages, averages, or comparisons
    unless they are directly returned by a tool or can be calculated from
    the returned tool data. Clearly label calculated values.

15. When reporting facility information, keep each value tied to its source
    table and do not merge metrics from different tables into a single
    unsupported metric.

16. Do not turn analytical findings into new operational recommendations.
    Only report recommended actions that are explicitly provided by the
    authoritative data source. Prediction disagreements may be described
    as a diagnostic finding, but do not claim their cause or recommend
    model changes, data changes, investigations, or mitigation strategies
    unless the data explicitly provides that recommendation.

17. When comparing two facilities, report:
    - each facility's priority rank and priority level
    - which facility has the higher current priority
    - high-risk alert counts
    - authoritative avg_risk_score
    - recommended action for each facility
    Keep every metric tied to facility_final_priorities.

18. When reporting an all-facilities executive health summary, organize each
    facility's information in this order:
    priority rank, priority level, high-risk alerts, authoritative
    avg_risk_score, prediction disagreements, and stored recommended action.
    For prediction disagreements, describe them only as cases where the
    stored predicted_risk_event conflicts with the calculated P(event=1).
    Do not infer causes or additional recommendations.

19. If a tool reports that a facility was not found, clearly state that the
    facility does not exist in the returned authoritative data. Do not
    interpret missing data as zero alerts, zero risk, or zero disagreements,
    and do not invent facility information.

Be concise but provide enough evidence for an executive decision.
""",
        tools=[
        FunctionTool(get_facility_priorities),
        FunctionTool(compare_facilities),
        FunctionTool(get_facility_health),
        FunctionTool(get_all_facilities_health),
        FunctionTool(get_facility_alerts),
        FunctionTool(get_top_risks),
        FunctionTool(analyze_prediction_disagreements),
    ],
)