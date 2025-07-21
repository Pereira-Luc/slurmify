import time
import streamlit as st

import requests
import json

from streamlit_functions.code_display import display_code
from streamlit_functions.job_status import display_job_status, get_job_status
from streamlit_functions.requirments_config import requirments_config
from streamlit_functions.account_config import account_prompt
from streamlit_functions.func import (
    get_job_information,
    get_layout,
    init_states,
    print_all_states,
    submit_slurm_job,
    cancel_job,
)
from streamlit_functions.resources_config import resource_config_prompt


def setup_page():
    st.set_page_config(layout="wide")
    return


# right_layout.success("Job submitted successfully!")
def run_display_job_status(status_placeholder):

    for _ in range(
        100
    ):  # need to change this to when job failed or complet canceld malybe somthing else

        get_job_information(
            jwt_token=st.session_state.selected_JWT_token,
            job_id=st.session_state.job_id,
        )

        with status_placeholder.container():

            job_stats = get_job_status(st.session_state.job_data)

            if job_stats is None:
                status_placeholder.warning("No job information available")
                break

            if job_stats["job_state"] == "COMPLETED":
                display_job_status(st.session_state.job_data)
                break

            if job_stats["job_state"] == "FAILED":
                display_job_status(st.session_state.job_data)
                break

            if job_stats["job_state"] == "CANCELLED":
                display_job_status(st.session_state.job_data)
                break

            display_job_status(st.session_state.job_data)

        time.sleep(5)
        # Button to cancel the job


def main_tab_content():
    left_layout, right_layout = get_layout()

    left_layout.title("Slurmify")
    left_layout.markdown(
        """ 
        Use this app to submit jobs to a Slurm cluster.
        """
    )

    left_layout.markdown(
        """
        ### Select the account to use
        """
    )

    account_prompt(left_layout)
    resource_config_prompt(left_layout)
    requirments_config(left_layout)

    slurm, job = display_code(right_layout)
    # print_all_states()

    right_layout.download_button(
        label="Download Slurm Script",
        data=slurm,
        file_name=f"{job.name}.sh",
        mime="text/x-sh",
    )

    if right_layout.button(label="Submit Job", args=(job.name)):
        submit_slurm_job(
            jwt_token=st.session_state.selected_JWT_token,
            job=job,
            slurm=slurm,
            layout=right_layout,
        )

    if st.session_state.job_id:
        status_placeholder = right_layout.empty()
        if right_layout.button(label="Cancel Job", key="cancel_job"):
            print("Cancelling job...")
            cancel_job(
                jwt_token=st.session_state.selected_JWT_token,
                job_id=st.session_state.job_id,
            )
            st.success("Job cancelled successfully!")

        run_display_job_status(status_placeholder)


def ai_chat_tab_content():
    st.title("AI Assistant (ALPHA)")
    st.markdown(
        """
    Welcome to the SLURM AI Assistant.
    
    You can:
    - Ask questions about SLURM configuration
    - Get help with job parameters
    - Receive recommendations for job optimization
    - Debug common issues
    
    - **Note:** This is an experimental feature and may not always provide accurate answers.
    - **Disclaimer:** The AI assistant is powered by an external service and may not always be available.
    """
    )

    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Genrate a random sessionID for chat
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(int(time.time() * 1000))

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            # st.markdown(f"**You:** {message['content']}")
            with st.chat_message("user"):
                st.write(f"{message['content']}")
        else:
            with st.chat_message("assistant"):
                st.write(f"{message['content']}")

    # User input area
    user_input = st.text_input("Ask me anything about SLURM:", key="ai_chat_input")

    # Send button
    if st.button("Send", key="send_chat"):
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )

            # Show a spinner while waiting for response
            with st.spinner("AI is thinking..."):
                try:
                    # Send request to n8n webhook
                    webhook_url = "http://10.40.0.56:5678/webhook/6908685f-995a-4003-9c6c-1dc71b53c3a5"
                    # webhook_url = "http://0.0.0.0:5678/webhook-test/6908685f-995a-4003-9c6c-1dc71b53c3a5"
                    payload = {
                        "message": user_input,
                        "session_id": st.session_state.session_id,
                        "history": st.session_state.chat_history[
                            :-1
                        ],  # Send previous history
                    }

                    response = requests.post(
                        webhook_url,
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(payload),
                        timeout=300,  # Set a reasonable timeout
                    )

                    if response.status_code == 200:
                        # Process successful response
                        try:
                            print("AI raw response:", response.text)
                            result = response.json()

                            # Handle response format [{'output': '...'}]
                            ai_response = ""
                            if (
                                isinstance(result, list)
                                and len(result) > 0
                                and "output" in result[0]
                            ):
                                ai_response = result[0]["output"]
                            else:
                                ai_response = result.get(
                                    "response",
                                    "I couldn't generate a response. Please try again.",
                                )

                            # Remove thinking section if present
                            if "<think>" in ai_response and "</think>" in ai_response:
                                thinking_start = ai_response.find("<think>")
                                thinking_end = ai_response.find("</think>") + len(
                                    "</think>"
                                )
                                ai_response = (
                                    ai_response[:thinking_start]
                                    + ai_response[thinking_end:]
                                )
                                ai_response = ai_response.strip()

                            # Add AI response to chat history
                            st.session_state.chat_history.append(
                                {"role": "assistant", "content": ai_response}
                            )
                            st.rerun()
                        except json.JSONDecodeError:
                            st.error("Received invalid response from AI service")
                    else:
                        st.error(
                            f"Error communicating with AI service: Status code {response.status_code}"
                        )

                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to AI service: {str(e)}")

    # Clear chat button
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


def start_server():
    init_states()
    setup_page()

    # Create tabs
    main_tab, ai_chat_tab = st.tabs(["Job Configuration", "AI Assistant"])

    # Fill the tabs with content
    with main_tab:
        main_tab_content()

    with ai_chat_tab:
        ai_chat_tab_content()


if __name__ == "__main__":
    start_server()
