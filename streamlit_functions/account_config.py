import streamlit as st


def account_prompt(layout):
    """Account configuration page."""

    layout.text_input("User", st.session_state.username, placeholder="", key="username")

    # Update workdir to include the username
    st.session_state.selected_workdir = f"/home/users/{st.session_state.username}"

    layout.text_input(
        "Workdir",
        st.session_state.selected_workdir,
        placeholder="",
        key="workdir",
    )

    layout.text_input("Account", st.session_state.selected_account, key="account")

    layout.text_input("Job Name", st.session_state.job_name, key="job_name")

    # Update the logs default and error paths to include the job name
    st.session_state.selected_logs_default = f"{st.session_state.job_name}-%j.out"
    st.session_state.selected_logs_error = f"{st.session_state.job_name}-%j.err"

    layout.text_input(
        "JWT Token: Required to submit job",
        st.session_state.selected_JWT_token,
        key="selected_JWT_token",
    )

    layout.divider()
