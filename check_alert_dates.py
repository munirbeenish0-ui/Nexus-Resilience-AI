from google.cloud import bigquery

client = bigquery.Client(project="nexus-resilience-ai")

query = """
SELECT
    column_name,
    data_type
FROM `nexus-resilience-ai.nexus_resilience.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'nexus_risk_alerts'
ORDER BY ordinal_position
"""

for row in client.query(query).result():
    print(row["column_name"], "|", row["data_type"])