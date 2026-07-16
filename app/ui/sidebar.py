from typing import Tuple

import streamlit as st

from app.auth.roles import RoleManager


def initialize_sidebar_state() -> None:
    if "selected_display_role" not in st.session_state:
        st.session_state.selected_display_role = "Employee"

    if "active_role" not in st.session_state:
        st.session_state.active_role = "employee"


def render_sidebar() -> Tuple[str, bool]:
    """
    Render the application sidebar.

    Returns:
        tuple:
            - normalized internal role
            - True when the user requests conversation clearing
    """

    initialize_sidebar_state()

    with st.sidebar:
        st.title("FinSolve AI")
        st.caption("Role-Based Company Knowledge Assistant")

        st.divider()

        display_roles = RoleManager.get_display_roles()
        current_display_role = st.session_state.selected_display_role

        try:
            default_index = display_roles.index(current_display_role)
        except ValueError:
            default_index = 0

        selected_display_role = st.selectbox(
            label="Select your role",
            options=display_roles,
            index=default_index,
            key="role_selector",
        )

        selected_internal_role = RoleManager.get_internal_role(
            selected_display_role
        )

        role_changed = (
            selected_internal_role != st.session_state.active_role
        )

        if role_changed:
            st.session_state.selected_display_role = selected_display_role
            st.session_state.active_role = selected_internal_role

        # Removed the long role-description box.

        st.write(
            f"**Active role:** `{selected_internal_role}`"
        )

        if selected_internal_role == "c_level":
            st.success("Full company access enabled.")
        else:
            st.warning(
                "Search results are restricted to your assigned department."
            )

        st.divider()

        clear_requested = st.button(
            "Clear conversation",
            use_container_width=True,
            type="secondary",
        )

        st.divider()

        st.markdown("### Available departments")

        st.markdown(
            """
            - General company information
            - Finance
            - Marketing
            - Human Resources
            - Engineering
            """
        )

        st.caption(
            "Unauthorized documents are filtered before they are sent "
            "to the language model."
        )

    return selected_internal_role, clear_requested