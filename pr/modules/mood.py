import streamlit as st
import datetime
from auth import load_users, save_users # Import functions from auth.py

def mood_page(username):
    """
    Displays the mood tracker page for the logged-in user.
    Allows users to log their mood and view recent mood history.
    """
    st.title(f"🧠 {username}'s Mood Tracker")

    users = load_users()
    user_data = users.get(username, {})
    user_moods = user_data.get("moods", [])

    # --- Log New Mood ---
    st.header("How are you feeling today?")
    
    mood_options = {
        "Happy": "😀",
        "Sad": "😢",
        "Angry": "😡",
        "Stressed": "😣",
        "Anxious": "😰",
        "Excited": "🤩",
        "Neutral": "😐"
    }

    # Create buttons for mood selection
    selected_mood_text = st.radio(
        "Select your mood:",
        list(mood_options.keys()),
        index=6, # Default to Neutral
        horizontal=True
    )
    selected_mood_emoji = mood_options[selected_mood_text]

    mood_description = st.text_area("Optional: Describe why you feel this way (e.g., 'Had a great day at work!')", max_chars=200)

    if st.button("Log Mood"):
        new_mood_entry = {
            "timestamp": datetime.datetime.now().isoformat(), # ISO format for easy storage and retrieval
            "mood_text": selected_mood_text,
            "mood_emoji": selected_mood_emoji,
            "description": mood_description
        }
        user_moods.append(new_mood_entry)
        user_data["moods"] = user_moods
        users[username] = user_data
        save_users(users)
        st.success(f"Your mood '{selected_mood_text} {selected_mood_emoji}' has been logged!")
        st.rerun() # Rerun to update the displayed history

    st.markdown("---")

    # --- Recent Mood History ---
    st.header("Your Recent Mood History")

    if not user_moods:
        st.info("You haven't logged any moods yet. Log one above!")
    else:
        # Display moods in reverse chronological order (most recent first)
        recent_moods = sorted(user_moods, key=lambda x: x["timestamp"], reverse=True)

        # Show only the last 10 entries for brevity, or all if less than 10
        display_count = st.slider("Show last X entries:", 1, len(recent_moods), min(10, len(recent_moods)))
        
        for entry in recent_moods[:display_count]:
            timestamp_dt = datetime.datetime.fromisoformat(entry["timestamp"])
            st.write(f"**{timestamp_dt.strftime('%Y-%m-%d %H:%M')}** - {entry['mood_emoji']} {entry['mood_text']}")
            if entry["description"]:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*\"{entry['description']}\"*")
            st.markdown("---")

