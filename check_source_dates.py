from google.cloud import bigquery

client = bigquery.Client(project="nexus-resilience-ai")

queries = {
    "nexus_risk_alerts": """
        SELECT
            facility,
            COUNT(*) AS records,
            COUNTIF(risk_level = 'HIGH') AS high_risk_records,
            COUNTIF(risk_level = 'MEDIUM') AS medium_risk_records
        FROM `nexus-resilience-ai.nexus_resilience.nexus_risk_alerts`
        GROUP BY facility
        ORDER BY facility
    """,

    "facility_final_priorities": """
        SELECT
            facility,
            priority_rank,
            priority_level,
            avg_risk_score,
            high_risk_alerts,
            recommended_action
        FROM `nexus-resilience-ai.nexus_resilience.facility_final_priorities`
        ORDER BY priority_rank
    """
}

for name, query in queries.items():
    print(f"\n--- {name} ---")
    for row in client.query(query).result():
        print(dict(row))