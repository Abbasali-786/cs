import streamlit as st
import datetime
import random # For optional prompts
from auth import load_users, save_users # Import functions from auth.py
import os
from groq import Groq

# Function to get AI reflection using Groq API
def get_ai_reflection(journal_entry):
    # Get API key from environment variables
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "Groq API key not found in environment variables. Please set the 'GROQ_API_KEY' environment variable."
    
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate and empathetic AI. Provide a gentle, supportive, and reflective response to the user's journal entry. Keep it concise and encouraging, focusing on emotional well-being. Do not offer advice unless explicitly asked, instead, reflect on their feelings. If the entry is short, you can ask a gentle follow-up question."
                },
                {
                    "role": "user",
                    "content": f"My journal entry: {journal_entry}"
                }
            ],
            model="llama-3.3-70b-versatile", # Using the model specified by the user
            temperature=0.7, # Adjust for creativity
            max_tokens=150 # Limit response length
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error getting AI reflection: {e}. Please ensure your 'GROQ_API_KEY' is correct and you have an internet connection."


def journal_page(username):
    """
    Provides a safe space for users to write journal entries.
    Allows users to write, save, and view their entries.
    """
    st.title(f"📓 {username}'s Digital Confessional")

    users = load_users()
    user_data = users.get(username, {})
    user_journals = user_data.get("journals", [])

    # --- Write New Journal Entry ---
    st.header("Write Your Entry")

    reflection_prompts = [
        "What's on your mind today?",
        "How are you truly feeling right now?",
        "What's one thing you're grateful for today?",
        "What challenged you today, and how did you overcome it?",
        "If you could tell your past self one thing, what would it be?",
        "What is one small victory you had today?",
        "What are you looking forward to tomorrow?"
    ]

    # Optional prompt
    if st.checkbox("Show me a reflection prompt"):
        st.info(random.choice(reflection_prompts))

    journal_entry_text = st.text_area(
        "Pour your heart out here...",
        height=200,
        help="This is a private space for your thoughts and feelings.",
        key="current_journal_entry" # Added a key for consistent behavior
    )

    col_save, col_ai = st.columns([1, 1])

    with col_save:
        if st.button("Save Entry"):
            if journal_entry_text.strip():
                new_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "content": journal_entry_text.strip()
                }
                user_journals.append(new_entry)
                user_data["journals"] = user_journals
                users[username] = user_data
                save_users(users)
                st.success("Your entry has been saved!")
                st.rerun() # Rerun to update the displayed history
            else:
                st.warning("Please write something before saving your entry.")
    
    st.markdown("---")

    # --- AI Reflection Section ---
    st.subheader("AI Reflection")
    # Removed st.text_input for API key

    with col_ai:
        if st.button("Get AI Reflection", disabled=not journal_entry_text.strip()):
            if journal_entry_text.strip():
                with st.spinner("Generating AI reflection..."):
                    # Call get_ai_reflection without passing API key, it will read from env
                    reflection = get_ai_reflection(journal_entry_text.strip())
                    st.session_state.ai_reflection = reflection # Store reflection in session state
            else:
                st.warning("Please write a journal entry first to get an AI reflection.")
    
    if "ai_reflection" in st.session_state and st.session_state.ai_reflection:
        st.info(st.session_state.ai_reflection)
        # Clear reflection after displaying, or keep it if user wants to see it persist
        # del st.session_state.ai_reflection # Uncomment if you want it to disappear on next rerun


    st.markdown("---")

    # --- Recent Journal History ---
    st.header("Your Past Entries")

    if not user_journals:
        st.info("You haven't written any journal entries yet. Start by writing one above!")
    else:
        # Display entries in reverse chronological order (most recent first)
        recent_entries = sorted(user_journals, key=lambda x: x["timestamp"], reverse=True)

        # Show a slider for number of entries to display
        display_count = st.slider("Show last X entries:", 1, len(recent_entries), min(5, len(recent_entries)))

        for entry in recent_entries[:display_count]:
            timestamp_dt = datetime.datetime.fromisoformat(entry["timestamp"])
            st.write(f"**{timestamp_dt.strftime('%Y-%m-%d %H:%M')}**")
            st.markdown(f"```\n{entry['content']}\n```") # Display content in a code block for better formatting
            st.markdown("---")

