WITH daily_metrics AS (
    SELECT
        metric_date,
        day_of_week,
        steps,
        sleep_hours,
        workout_completed,
        workout_minutes,
        mood_score,
        energy_level,
        weight_lbs,
        hrv,
        -- Calculate moving averages (7-day)
        AVG(steps) OVER (ORDER BY metric_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as steps_7day_avg,
        AVG(sleep_hours) OVER (ORDER BY metric_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as sleep_7day_avg,
        AVG(mood_score) OVER (ORDER BY metric_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as mood_7day_avg,
        AVG(weight_lbs) OVER (ORDER BY metric_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as weight_7day_avg,
        -- week over week changes
        LAG(steps, 7) OVER (ORDER BY metric_date) as steps_last_week,
        LAG(weight_lbs, 7) OVER (ORDER BY metric_date) as weight_last_week
    FROM {{ ref('stg_health_metrics')}}
)

SELECT
    *,
    CASE
        WHEN steps_last_week IS NOT NULL
        THEN ROUND(((steps - steps_last_week) / steps_last_week) * 100, 1)
    END as steps_wow_change_pct,
    CASE
        WHEN weight_last_week IS NOT NULL
        THEN ROUND(weight_lbs - weight_last_week, 1)
    END as weight_wow_change_lbs,
    ROUND((
        (steps / 10000.0 * 3) +
        (sleep_hours / 8.0 * 2) +
        (workout_completed * 2) +
        (mood_score / 10.0 * 3)
    ), 1) as daily_health_score
FROM daily_metrics
ORDER BY metric_date DESC