import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
import random 

np.random.seed(42)
random.seed(42)

#generate 6 months of daily health data
end_date = datetime.now()
start_date = end_date - timedelta(days=180)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

health_data = []

#baseline metrics (will vary throughout the period)
base_steps = 8000
base_sleep_hours = 7.5
base_workout_minutes = 30

for date in date_range:
    day_of_week = date.dayofweek 
#steps - higher on weekdays, lower on weekends
    if day_of_week < 5: 
        steps = int(base_steps + np.random.normal(2000, 1500))
    else:
        steps = int(base_steps + np.random.normal(-1000, 1000))
    steps = max(steps, 1000)

    #sleep - varies based on day
    if day_of_week == 6:
        sleep_hours = base_sleep_hours + np.random.normal(1, 0.5)
    elif day_of_week == 4:
        sleep_hours = base_sleep_hours + np.random.normal(-0.5, 0.5)
    else:
        sleep_hours = base_sleep_hours + np.random.normal(0, 0.7)
    sleep_hours = round(max(min(sleep_hours, 10), 4), 1)

    #workout - more likely on certain days
    workout_probability = 0.7 if day_of_week in [1, 3, 5] else 0.3
    did_workout = random.random() < workout_probability

    if did_workout:
        workout_minutes = int(base_workout_minutes + np.random.normal(15, 10))
        workout_type = random.choice(['Running', 'Gym', 'Yoga', 'Cycling', 'Swimming'])
        calories_burned = workout_minutes * random.uniform(8, 12)
    else:
        workout_minutes = 0
        workout_type = None 
        calories_burned = 0 

    #mood - affected by sleep and exercise
    mood_base = 7 #scale from 1-10
    if sleep_hours >= 7.5:
        mood_base += 1
    if sleep_hours < 6:
        mood_base -= 1.5
    if did_workout:
        mood_base += 0.5
    
    mood = round(max(min(mood_base + np.random.normal(0, 1), 10), 1), 1)

    #energy level - correlated with sleep and mood
    energy = round(max(min(mood + np.random.normal(0, 0.5), 10), 1), 1)

    #water intake (glasses)
    water_glasses = int(max(6 + np.random.normal(2, 2), 2))

    #weight - gradual change over time
    days_elapsed = (date - start_date).days 
    weight_trend = -0.02* days_elapsed #slight downward trend
    weight = 170 + weight_trend + np.random.normal(0, 0.5)

    #heart rate variability (HRV) - indicator of recovery
    hrv = int(50 + (sleep_hours - 7) * 5 + np.random.normal(0, 10))
    hrv = max(min(hrv, 100), 20)

    health_data.append({
        'date': date.strftime('%Y-%m-%d'),
        'steps': steps,
        'distance_miles': round(steps * 0.0004, 2), #rough conversion
        'active_minutes': workout_minutes + int(steps / 100), #active calories
        'sleep_hours': sleep_hours,
        'sleep_quality': round(min(sleep_hours / 8 * 10, 10), 1),
        'workout_minutes': workout_minutes,
        'workout_type': workout_type,
        'calories_burned': int(calories_burned),
        'mood_score': mood,
        'energy_level': energy,
        'water_glasses': water_glasses,
        'weight_lbs': round(weight, 1),
        'resting_heart_rate': int(60 + np.random.normal(0, 5)),
        'hrv': hrv,
        'day_of_week': date.strftime('%A')
    })

df = pd.DataFrame(health_data)

print(f"Generated {len(df)} days of health data")
print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
print(f'\nAverage metrics:')
print(f"  Steps: {df['steps'].mean():.0f}")
print(f"  Mood: {df['mood_score'].mean():.1f}/10")
print(f"  Workouts: {df[df['workout_minutes'] > 0].shape[0]} days")

df.to_csv('../data/health_metrics.csv', index=False)
print("\nData saved to data/health_metrics.csv")


