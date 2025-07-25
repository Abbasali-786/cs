import streamlit as st
import uuid # For generating unique IDs for goals
from auth import load_users, save_users # Import functions from auth.py

def goal_page(username):
    """
    Displays the goal management page for the logged-in user.
    Allows users to add, view, edit, and delete goals.
    """
    st.title(f"🎯 {username}'s Goals")

    users = load_users()
    user_data = users.get(username, {})
    user_goals = user_data.get("goals", [])

    # --- Add New Goal ---
    st.header("Add a New Goal")
    with st.form("add_goal_form", clear_on_submit=True):
        goal_title = st.text_input("Goal Title", max_chars=100, help="e.g., Finish Hackathon Project")
        goal_description = st.text_area("Description (Optional)", help="Provide more details about your goal.")
        goal_due_date = st.date_input("Due Date (Optional)", help="When do you plan to achieve this goal?")
        goal_status = st.selectbox("Status", ["To Do", "In Progress", "Completed", "Cancelled"], index=0)

        submitted = st.form_submit_button("Add Goal")
        if submitted:
            if goal_title:
                new_goal = {
                    "id": str(uuid.uuid4()), # Unique ID for the goal
                    "title": goal_title,
                    "description": goal_description,
                    "due_date": str(goal_due_date) if goal_due_date else None,
                    "status": goal_status
                }
                user_goals.append(new_goal)
                user_data["goals"] = user_goals
                users[username] = user_data
                save_users(users)
                st.success("Goal added successfully!")
                st.rerun() # Rerun to update the displayed goals
            else:
                st.error("Goal Title cannot be empty.")

    st.markdown("---")

    # --- View and Manage Goals ---
    st.header("Your Current Goals")

    if not user_goals:
        st.info("You haven't set any goals yet. Add one above!")
    else:
        # Filter and sort options
        status_filter = st.sidebar.multiselect("Filter by Status", ["To Do", "In Progress", "Completed", "Cancelled"], default=["To Do", "In Progress"])
        sort_by = st.sidebar.selectbox("Sort by", ["None", "Due Date (Asc)", "Due Date (Desc)", "Status"])

        filtered_goals = [goal for goal in user_goals if goal["status"] in status_filter]

        if sort_by == "Due Date (Asc)":
            filtered_goals.sort(key=lambda x: (x["due_date"] is None, x["due_date"]))
        elif sort_by == "Due Date (Desc)":
            filtered_goals.sort(key=lambda x: (x["due_date"] is None, x["due_date"]), reverse=True)
        elif sort_by == "Status":
            # Define a custom order for status
            status_order = {"To Do": 0, "In Progress": 1, "Completed": 2, "Cancelled": 3}
            filtered_goals.sort(key=lambda x: status_order.get(x["status"], 99))


        for i, goal in enumerate(filtered_goals):
            expander_title = f"**{goal['title']}** - Status: {goal['status']}"
            if goal['due_date']:
                expander_title += f" (Due: {goal['due_date']})"

            with st.expander(expander_title):
                st.write(f"**Description:** {goal['description'] if goal['description'] else 'No description provided.'}")
                st.write(f"**Status:** {goal['status']}")
                st.write(f"**Due Date:** {goal['due_date'] if goal['due_date'] else 'Not set'}")

                col1, col2 = st.columns(2)

                # Edit Goal
                with col1:
                    if st.button(f"Edit Goal", key=f"edit_{goal['id']}"):
                        st.session_state.editing_goal_id = goal['id']
                        st.rerun() # Rerun to show edit form

                # Delete Goal
                with col2:
                    if st.button(f"Delete Goal", key=f"delete_{goal['id']}"):
                        # Implement a confirmation dialog if needed in a real app
                        # For now, directly delete
                        user_goals.remove(goal)
                        user_data["goals"] = user_goals
                        users[username] = user_data
                        save_users(users)
                        st.success("Goal deleted successfully!")
                        st.rerun() # Rerun to update the displayed goals

        # --- Edit Goal Form (appears when a goal is selected for editing) ---
        if "editing_goal_id" in st.session_state and st.session_state.editing_goal_id:
            goal_to_edit = next((g for g in user_goals if g["id"] == st.session_state.editing_goal_id), None)

            if goal_to_edit:
                st.markdown("---")
                st.header(f"Edit Goal: {goal_to_edit['title']}")
                with st.form("edit_goal_form", clear_on_submit=False):
                    edited_title = st.text_input("Goal Title", value=goal_to_edit['title'], key="edit_title")
                    edited_description = st.text_area("Description", value=goal_to_edit['description'], key="edit_description")
                    
                    # Convert string date back to date object for st.date_input
                    import datetime
                    initial_date = None
                    if goal_to_edit['due_date']:
                        try:
                            initial_date = datetime.datetime.strptime(goal_to_edit['due_date'], "%Y-%m-%d").date()
                        except ValueError:
                            initial_date = None # Handle invalid date format

                    edited_due_date = st.date_input("Due Date", value=initial_date, key="edit_due_date")
                    
                    # Find the index of the current status for the selectbox
                    status_options = ["To Do", "In Progress", "Completed", "Cancelled"]
                    initial_status_index = status_options.index(goal_to_edit['status']) if goal_to_edit['status'] in status_options else 0
                    edited_status = st.selectbox("Status", status_options, index=initial_status_index, key="edit_status")

                    update_submitted = st.form_submit_button("Update Goal")
                    cancel_edit = st.form_submit_button("Cancel Edit")

                    if update_submitted:
                        if edited_title:
                            # Update the goal in the list
                            for i, g in enumerate(user_goals):
                                if g["id"] == goal_to_edit["id"]:
                                    user_goals[i]["title"] = edited_title
                                    user_goals[i]["description"] = edited_description
                                    user_goals[i]["due_date"] = str(edited_due_date) if edited_due_date else None
                                    user_goals[i]["status"] = edited_status
                                    break
                            user_data["goals"] = user_goals
                            users[username] = user_data
                            save_users(users)
                            st.success("Goal updated successfully!")
                            st.session_state.editing_goal_id = None # Clear editing state
                            st.rerun()
                        else:
                            st.error("Goal Title cannot be empty.")
                    elif cancel_edit:
                        st.session_state.editing_goal_id = None # Clear editing state
                        st.rerun()
            else:
                st.error("Goal to edit not found.")
                st.session_state.editing_goal_id = None # Clear editing state

