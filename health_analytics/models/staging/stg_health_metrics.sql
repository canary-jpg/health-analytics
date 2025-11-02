SELECT
    date::DATE as metric_date,
    steps,
    distance_miles,
    active_minutes,
    sleep_hours,
    sleep_quality,
    workout_minutes,
    workout_type,
    calories_burned,
    mood_score,
    energy_level,
    water_glasses,
    weight_lbs,
    resting_heart_rate,
    hrv,
    day_of_week,
    CASE WHEN workout_minutes > 0 THEN 1 ELSE 0 END as workout_completed
FROM raw_health_metrics