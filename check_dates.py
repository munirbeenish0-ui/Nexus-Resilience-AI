from google.cloud import bigquery

client = bigquery.Client(project="nexus-resilience-ai")

query = """
SELECT
    MIN(date) AS min_date,
    MAX(date) AS max_date,
    COUNT(DISTINCT date) AS distinct_dates
FROM `nexus-resilience-ai.nexus_resilience.risk_predictions`
"""

row = list(client.query(query).result())[0]

print("min_date:", row["min_date"])
print("max_date:", row["max_date"])
print("distinct_dates:", row["distinct_dates"])