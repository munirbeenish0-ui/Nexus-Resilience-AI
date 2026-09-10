from google.cloud import bigquery

client = bigquery.Client(project="nexus-resilience-ai")

query = """
SELECT
    facility,
    MIN(date) AS first_date,
    MAX(date) AS last_date,
    COUNT(*) AS records
FROM `nexus-resilience-ai.nexus_resilience.risk_predictions`
GROUP BY facility
ORDER BY facility
"""

for row in client.query(query).result():
    print(
        row["facility"],
        "| first:", row["first_date"],
        "| last:", row["last_date"],
        "| records:", row["records"]
    )