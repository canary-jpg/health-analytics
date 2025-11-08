import streamlit as st 
import duckdb
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go 
from datetime import datetime, timedelta 

st.set_page_config(page_title="Health Analytics Dashboard", page_icon="🏃🏾‍♀️‍➡️", layout="wide")

#connect to DuckDB
@st.cache_resource
def get_connection():
    return duckdb.connect("../health_analytics/health_analytics.duckdb", read_only=True)

@st.cache_data(ttl=600)
def load_data(query):
    conn = get_connection()
    return conn.execute(query).df()

st.title("🏃🏾‍♀️‍➡️ Personal Health Analytics Dashboard")
st.markdown("---")

#load data
daily_summary = load_data("SELECT * FROM daily_health_summary ORDER BY metric_date DESC")
correlations = load_data("SELECT * FROM health_correlations")
workout_recs = load_data("SELECT * FROM workout_recommendations ORDER BY optimal_workout_score DESC")
personal_records = load_data("SELECT * FROM personal_records")

#convert date column
daily_summary['metric_date'] = pd.to_datetime(daily_summary['metric_date'])

#current metrics (most recent day)
latest = daily_summary.iloc[0]

#key metrics row
st.subheader("📊 Today's Snapshot")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Steps",
        f"{int(latest['steps']):,}",
        f"{latest['steps_wow_change_pct']:.1f}% vs last week" if pd.notna(latest['steps_wow_change_pct']) else None

    )

with col2:
    st.metric(
        "Sleep",
        f"{latest['sleep_hours']:.1f} hrs"
        "🟢 Goog" if latest['sleep_hours'] >= 7.5 else "🟡 Low"
    )

with col3:
    st.metric(
        "Workout"
        "✅ Done" if latest['workout_completed'] == 1 else "❌ Skipped",
        f"{int(latest['workout_minutes'])} min" if latest['workout_completed'] else None
    )

with col4:
    st.metric(
        "Mood",
        f"{latest['mood_score']:.1f}/10",
        f"Avg: {daily_summary['mood_score'].mean():.1f}"

    )

with col5:
    st.metric(
        "Health Score",
        f"{latest['daily_health_score']:.1f}/10",
        "Overall Wellness"
    )

st.markdown("---")

#trends over time
st.subheader("📈 Trends (Last 90 Days)")

#filtering to the last 90 days
last_90 = daily_summary[daily_summary['metric_date'] >= datetime.now() - timedelta(days=90)]
tab1, tab2, tab3, tab4 = st.tabs(["Steps & Activity", "Sleep & Mood", "Weight", "Health Score"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=last_90['metric_date'],
        y=last_90['steps'],
        name='Daily Steps',
        line=dict(color='blue', width=1),
        opacity=0.6
    ))
    fig.add_trace(go.Scatter(
        x=last_90['metric_date'],
        y=last_90['steps_7day_avg'],
        name='7-Day Average',
        line=dict(color='blue', width=3)
    ))
    fig.add_hline(y=10000, line_dash="dash", line_color="green", annotation_text="10k Goal")
    fig.update_layout(height=400, hovermode='x unified', yaxis_title='Steps')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=last_90['metric_date'],
        y=last_90['sleep_hours'],
        name='Sleep Hours',
        yaxis='y',
        line=dict(color='purple')
    ))
    fig.add_trace(go.Scatter(
        x=last_90['metric_date'],
        y=last_90['mood_score'],
        name='Mood Score',
        yaxis='y2',
        line=dict(color='orange')
    ))
    fig.update_layout(
        height=400,
        hovermode='x unified',
        yaxis=dict(title='Sleep Hours', range=[0, 10]),
        yaxis2=dict(title='Mood Score', overlaying='y', side='right', range=[0,10])
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=last_90['metric_date'],
        y=last_90['weight_lbs'],
        name='Daily Weight',
        mode='markers',
        marker=dict(size=4, color='lightblue')
    ))
    fig.add_trace(go.Scatter(
        x=last_90['metric_date'],
        y=last_90['weight_7day_avg'],
        name='7-Day Trend',
        line=dict(color='blue', width=3)
    ))
    fig.update_layout(height=400, hovermode='x unified', yaxis_title='Weight (lbs)')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    fig = px.line(
        last_90,
        x='metric_date',
        y='daily_health_score',
        title='Daily Health Score (Composite of steps, sleep, workout, mood)'
    )
    fig.add_hline(y=7, line_dash='dash', line_color='green', annotation_text='Target')
    fig.update_layout(height=400, yaxis_range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

#insights section
col1, col2 = st.columns(2)

with col1:
    st.subheader("💡 Health Correlations")

    for pair in correlations['correlation_pair'].unique():
        st.write(f"**{pair}**")
        pair_data = correlations[correlations['correlation_pair'] == pair]

        fig = px.bar(
            pair_data,
            x='category',
            y='avg_outcome',
            text='avg_outcome',
            color='avg_outcome',
            color_continuous_scale='RdYlGn'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(height=250, showlegend=False, xaxis_title='', yaxis_title='Outcome Score')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('🎯 Best Days to Workout')

    fig = px.bar(
        workout_recs,
        x='day_of_week',
        y='optimal_workout_score',
        color='recommendation',
        text='workout_completion_rate',
        color_discrete_map={
            'HIGHLY_RECOMMENDED': 'green',
            'RECOMMENDED': 'lightgreen',
            'OPTIONAL': 'yellow',
            'REST_DAY': 'orange'
        }
    )
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    fig.update_layout(height=400, xaxis_title='Day of Week', yaxis_title='Workout Score')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        workout_recs[['day_of_week', 'recommendation', 'avg_sleep_by_day', 'energy_boost_from_workout']].rename(columns={
            'day_of_week': 'Day',
            'recommendation': 'Recommendaion',
            'avg_sleep_by_day': 'Avg Sleep',
            'energy_boost_from_workout': 'Energy Boost'
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown('---')

#personal records
st.subheader('🏆 Personal Records')

col1, col2, col3 = st.columns(3)

records_list = personal_records.to_dict('records')

with col1:
    if len(records_list) > 0:
        record = records_list[0] #steps
        st.metric(
            "🚶🏾‍♂️‍➡️ " + record['metric'],
            f"{int(record['personal_best']):,}",
            f"Achieved: {record['achieved_date']}"
        )
        if record['current_value']:
            st.progress(record['pct_of_best'] / 100)
            st.caption(f"Currently at {record['pct_of_best']:.0f}% of best")

with col2:
    if len(records_list) > 1:
        record = records_list[1] # workout
        st.metric(
            "💪🏾 " + record['metric'],
            f"{int(record['personal_best'])} min",
            f"Achieved: {record['achieved_date']}"
        )

with col3:
    if len(records_list) > 2:
        record = records_list[2] #weight
        st.metric(
            "⚖️ " + record['metric'],
            f"{record['personal_best']:.1f} lbs",
            f"Achieved: {record['achieved_date']}"
        )
        if record['current_value']:
            diff = record['current_value'] - record['personal_best']
            st.caption(f"Currently: {record['current_value']:.1f} lb ({diff:+.1f})")

st.markdown('---')

#weekly summary
st.subheader("📆 This Week's Summary")

this_week = daily_summary[daily_summary['metric_date'] >= datetime.now() - timedelta(days=7)]

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_steps = this_week['steps'].mean()
    st.metric("Avg Daily Steps", f"{int(avg_steps):,}")

with col2:
    workouts = this_week['workout_completed'].sum()
    st.metric("Workouts Completed", f"{int(workouts)}/7")

with col3:
    avg_sleep = this_week['sleep_hours'].mean()
    st.metric('Avg Sleep', f"{avg_sleep:.1f} hrs")

with col4:
    avg_mood = this_week['mood_score'].mean()
    st.metric('Avg Mood', f"{avg_mood:.1f}/10")
    