-- analyze correlations between different health factors
WITH weekly_aggregates AS (
    SELECT
        DATE_TRUNC('week', metric_date) as week_start,
        AVG(steps) as avg_steps,
        AVG(sleep_hours) as avg_sleep,
        AVG(workout_minutes) as avg_workout,
        AVG(mood_score) as avg_mood,
        AVG(energy_level) as avg_energy,
        AVG(weight_lbs) as avg_weight,
        SUM(workout_completed) as workouts_per_week
    FROM {{ ref('stg_health_metrics') }}
    GROUP BY 1 
),

sleep_impact AS (
    SELECT
        'Sleep vs Mood' as correlation_pair,
        CASE
            WHEN avg_sleep >= 8 THEN 'High Sleep (8} hrs)'
            WHEN avg_sleep >= 7 THEN 'Medium Sleep (7-8 hrs)'
            ELSE 'Low Sleep (<7 hrs)'
        END as category,
        AVG(avg_mood) as avg_outcome,
        COUNT(*) as weeks 
    FROM weekly_aggregates
    GROUP BY 2
),

exercise_impact AS (
    SELECT
        'Exercise vs Energy' as correlation_pair,
        CASE
            WHEN workouts_per_week >= 4 THEN 'High Activity (4+ workouts)'
            WHEN workouts_per_week >= 2 THEN 'Medium Activity (2-3 workouts)'
            ELSE 'Low Activity (<2 workouts)'
        END as category,
        AVG(avg_energy) as avg_outcome,
        COUNT(*) as weeks 
    FROM weekly_aggregates
    GROUP BY 2
),

steps_impact AS (
    SELECT
        'Steps vs Mood' as correlation_pair,
        CASE
            WHEN avg_steps >= 10000 THEN 'High Steps (10k+)'
            WHEN avg_steps >= 7000 THEN 'Medium Steps (7-10k)'
            ELSE 'Low Steps (<7k)'
        END as category,
        AVG(avg_mood) as avg_outcome,
        COUNT(*) as weeks 
    FROM weekly_aggregates
    GROUP BY 2
    
)

SELECT * FROM sleep_impact
UNION ALL
SELECT * FROM exercise_impact
UNION ALL
SELECT * FROM steps_impact
ORDER BY correlation_pair, avg_outcome DESC