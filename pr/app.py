import streamlit as st
import os # Import the os module
from auth import login_or_register
from modules.goals import goal_page
from modules.mood import mood_page
from modules.journal import journal_page
from modules.dashboard import dashboard_page

def main():
    """Main function to run the SoulSync application."""
    # Load custom CSS using an absolute path for robustness
    # os.path.dirname(__file__) gets the directory of the current script (app.py)
    # os.path.join constructs a path safely across different operating systems
    css_file_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    try:
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: style.css not found at {css_file_path}. Please ensure it's in the 'assets' folder.")


    # Check if user is already logged in from session state
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    
    # Check if current_page is set in session state, default to "Goals"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Goals"

    user = st.session_state.logged_in_user

    if user is None:
        # If not logged in, show login/register page
        user = login_or_register()
        if user:
            st.session_state.logged_in_user = user # Store user in session state
            st.session_state.current_page = "Goals" # Default to Goals page after login
            st.rerun() # Rerun to switch to goal page
    else:
        # If logged in, show the main application pages
        st.sidebar.write(f"Logged in as: **{user}**")
        
        # Sidebar navigation
        app_menu = st.sidebar.radio(
            "Navigation",
            ["Goals", "Mood Tracker", "Journal", "Visual Dashboard"],
            index=["Goals", "Mood Tracker", "Journal", "Visual Dashboard"].index(st.session_state.current_page)
        )
        st.session_state.current_page = app_menu # Update current page in session state

        if st.sidebar.button("Logout"):
            st.session_state.logged_in_user = None
            st.session_state.login_menu = "Login" # Reset menu to login
            st.session_state.current_page = "Goals" # Reset page on logout
            st.rerun() # Rerun to go back to login page
        
        # Display the selected page
        if st.session_state.current_page == "Goals":
            goal_page(user)
        elif st.session_state.current_page == "Mood Tracker":
            mood_page(user)
        elif st.session_state.current_page == "Journal":
            journal_page(user)
        elif st.session_state.current_page == "Visual Dashboard":
            dashboard_page(user)


if __name__ == "__main__":
    main()
