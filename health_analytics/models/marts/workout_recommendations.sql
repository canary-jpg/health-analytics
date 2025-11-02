WITH recent_patterns AS (
    SELECT 
        day_of_week,
        AVG(CASE WHEN workout_completed = 1 THEN energy_level END) as avg_energy_after_workout,
        AVG(CASE WHEN workout_completed = 0 THEN energy_level END) as avg_energy_no_workout,
        AVG(sleep_hours) as avg_sleep_by_day,
        AVG(mood_score) as avg_mood_by_day,
        SUM(workout_completed) as total_workouts,
        COUNT(*) as total_days,
    FROM {{ ref('stg_health_metrics') }}
    WHERE metric_date > CURRENT_DATE - INTERVAL '90 days'
    GROUP BY 1
),

performance_by_day AS (
    SELECT
        *,
        ROUND(total_workouts::FLOAT / total_days * 100, 1) as workout_completion_rate,
        ROUND(avg_energy_after_workout - avg_energy_no_workout, 1) as energy_boost_from_workout
    FROM recent_patterns
)

SELECT 
    day_of_week,
    workout_completion_rate,
    avg_sleep_by_day,
    avg_mood_by_day,
    energy_boost_from_workout,
    --recommendation score (0 - 100)
    ROUND(
        (workout_completion_rate * 0.4) +
        (avg_sleep_by_day / 8 * 20) +
        (avg_mood_by_day * 2)
    , 0) as optimal_workout_score,
    --recommendation
    CASE
        WHEN workout_completion_rate > 70 AND avg_sleep_by_day >= 7.4 THEN 'HIGHLY_RECOMMENDED'
        WHEN workout_completion_rate > 50 THEN 'RECOMMENDED'
        WHEN avg_sleep_by_day < 6.5 THEN 'REST_DAY'
        ELSE 'OPTIONAL'
    END as recommendation
FROM performance_by_day
ORDER BY optimal_workout_score DESC 