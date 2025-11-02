import duckdb
import pandas as pd 

#connect to DuckDB
conn = duckdb.connect('health_analytics/health_analytics.duckdb')

#load csv data
df = pd.read_csv('data/health_metrics.csv')
print(f"Loading {len(df)} records into DuckDB...")

#drop and recreated
conn.execute("DROP TABLE IF EXISTS raw_health_metrics")
conn.register('df_view', df)
conn.execute("CREATE TABLE raw_health_metrics AS SELECT * FROM df_view")

#verify
count = conn.execute("SELECT COUNT(*) FROM raw_health_metrics").fetchone()[0]
print(f"Loaded {count} records")

#show sample
print("\nSample data:")
print(conn.execute("SELECT * FROM raw_health_metrics LIMIT 3").df())

#show summary stats
print("\nSummary statistics:")
print(conn.execute(""" 
    SELECT
        AVG(steps) as avg_steps,
        AVG(sleep_hours) as avg_sleep,
        AVG(mood_score) as avg_mood,
        COUNT(CASE WHEN workout_minutes > 0 THEN 1 ELSE 0 END) as workout_days
    FROM raw_health_metrics
""").df())

conn.close()