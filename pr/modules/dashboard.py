import streamlit as st
import pandas as pd
import datetime
from auth import load_users

def dashboard_page(username):
    """
    Displays the visual dashboard for the logged-in user.
    Includes mood trends, goal summaries, and placeholders for other insights.
    """
    st.title(f"📊 {username}'s Visual Dashboard")

    users = load_users()
    user_data = users.get(username, {})
    user_moods = user_data.get("moods", [])
    user_goals = user_data.get("goals", [])
    user_journals = user_data.get("journals", [])

    st.markdown("---")

    # --- Mood Trend Visualization ---
    st.header("Mood Trends Over Time")

    if not user_moods:
        st.info("No mood data available. Log your moods in the 'Mood Tracker' to see trends here!")
    else:
        # Map mood text to numerical values for charting
        mood_to_value = {
            "Happy": 5, "Excited": 4, "Neutral": 3,
            "Anxious": 2, "Stressed": 2, "Sad": 1, "Angry": 1
        }
        
        # Prepare data for DataFrame
        mood_data = []
        for entry in user_moods:
            try:
                timestamp_dt = datetime.datetime.fromisoformat(entry["timestamp"])
                mood_value = mood_to_value.get(entry["mood_text"], 0) # Default to 0 if mood not found
                mood_data.append({"Date": timestamp_dt.date(), "Time": timestamp_dt.time(), "Mood Value": mood_value, "Mood": entry["mood_text"]})
            except ValueError:
                st.warning(f"Could not parse timestamp: {entry['timestamp']}. Skipping this mood entry.")
                continue

        if mood_data:
            df_moods = pd.DataFrame(mood_data)
            df_moods["Datetime"] = df_moods.apply(lambda row: datetime.datetime.combine(row["Date"], row["Time"]), axis=1)
            df_moods = df_moods.sort_values(by="Datetime")

            st.write("### Your Mood Over Time")
            st.line_chart(df_moods.set_index("Datetime")["Mood Value"])

            st.write("### Daily Mood Distribution")
            # Group by date and count mood occurrences
            daily_mood_counts = df_moods.groupby(['Date', 'Mood']).size().unstack(fill_value=0)
            st.bar_chart(daily_mood_counts)

        else:
            st.info("No valid mood entries to display.")


    st.markdown("---")

    # --- Goal Achievement Summary ---
    st.header("Goal Progress Summary")

    if not user_goals:
        st.info("No goals set yet. Add goals in the 'Goals' section to see your progress here!")
    else:
        total_goals = len(user_goals)
        completed_goals = sum(1 for goal in user_goals if goal["status"] == "Completed")
        in_progress_goals = sum(1 for goal in user_goals if goal["status"] == "In Progress")
        to_do_goals = sum(1 for goal in user_goals if goal["status"] == "To Do")
        cancelled_goals = sum(1 for goal in user_goals if goal["status"] == "Cancelled")

        st.write(f"**Total Goals:** {total_goals}")
        st.write(f"**Completed:** {completed_goals}")
        st.write(f"**In Progress:** {in_progress_goals}")
        st.write(f"**To Do:** {to_do_goals}")
        st.write(f"**Cancelled:** {cancelled_goals}")

        # Create a simple pie chart for goal statuses
        goal_status_counts = pd.DataFrame({
            'Status': ['Completed', 'In Progress', 'To Do', 'Cancelled'],
            'Count': [completed_goals, in_progress_goals, to_do_goals, cancelled_goals]
        })
        # Filter out statuses with 0 count for better visualization
        goal_status_counts = goal_status_counts[goal_status_counts['Count'] > 0]

        if not goal_status_counts.empty:
            st.bar_chart(goal_status_counts.set_index('Status'))
        else:
            st.info("No goals with counts to display in the chart.")


    st.markdown("---")

    # --- Common Triggers from Journal Entries (Placeholder) ---
    st.header("Common Triggers & Insights from Journal Entries")
    if not user_journals:
        st.info("No journal entries available. Write some entries in the 'Journal' section to unlock insights here!")
    else:
        st.info("This section will analyze your journal entries to identify common themes, emotions, or triggers over time. (Coming Soon!)")
        st.markdown("*(Future features could include keyword extraction, sentiment analysis, and correlation with mood data.)*")

