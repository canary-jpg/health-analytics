WITH all_time_stats AS (
    SELECT
        MAX(steps) as max_steps,
        MAX(distance_miles) as max_distance,
        MAX(workout_minutes) as longest_workout,
        MAX(sleep_hours) as longest_sleep,
        MAX(mood_score) as best_mood,
        MAX(hrv) as max_hrv,
        MIN(weight_lbs) as lowest_weight,
        MIN(resting_heart_rate) as lowest_rhr
    FROM {{ ref('stg_health_metrics') }}
),

record_dates AS (
    SELECT
        (SELECT metric_date FROM {{ ref('stg_health_metrics') }} WHERE steps = a.max_steps LIMIT 1) as max_steps_date,
        (SELECT metric_date FROM {{ ref('stg_health_metrics') }} WHERE workout_minutes = a.longest_workout LIMIT 1) as longest_workout_date,
        (SELECT metric_date FROM {{ ref('stg_health_metrics') }} WHERE weight_lbs = a.lowest_weight LIMIT 1) as lowest_weight_date,
        a.*
    FROM all_time_stats a
),

current_stats AS (
    SELECT
        steps as current_steps,
        weight_lbs as current_weight,
        mood_score as current_mood
    FROM {{ ref('stg_health_metrics') }}
    ORDER BY metric_date DESC 
    LIMIT 1
)

SELECT
    'Steps' as metric,
    r.max_steps as personal_best,
    r.max_steps_date as achieved_date,
    c.current_steps as current_value,
    ROUND((c.current_steps::FLOAT / r.max_steps) * 100, 1) as pct_of_best
FROM record_dates r, current_stats c 

UNION ALL
SELECT
    'Workout Duration' as metric,
    r.longest_workout,
    r.longest_workout_date,
    NULL,
    NULL,
FROM record_dates r 

UNION ALL

SELECT
    'Workout Duration',
    r.longest_workout,
    r.longest_workout_date,
    NULL,
    NULL
FROM record_dates r 

UNION ALL 
SELECT 
    'Weight Loss',
    r.lowest_weight,
    r.lowest_weight_date,
    c.current_weight,
    ROUND(((r.lowest_weight - c.current_weight) / r.lowest_weight) * 100, 1) as pct_of_best
FROM record_dates r, current_stats c 