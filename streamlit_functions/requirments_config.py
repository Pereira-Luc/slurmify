import select
import streamlit as st
from utils.moduleListHandler import ModuleList, get_module_list


def available_modules():
    all_module: ModuleList = get_module_list()
    all_module_names = all_module.get_modules()
    return all_module_names


def available_modules_version(module_name: str):
    """Get available modules version."""
    all_module: ModuleList = get_module_list()
    all_module_versions = all_module.get_module_versions(module_name)
    return all_module_versions


def multi_select_modules(layout):
    """Multi select modules."""

    # Get available modules only once to avoid repeated calls
    modules = available_modules()

    # Use the multiselect with proper initialization
    selected = layout.multiselect(
        "Select Modules",
        options=modules,
        default=st.session_state.selected_modules,
        key="selected_modules",
    )

    # Convert selected modules to text format for the job script
    if selected:
        module_text = "\n".join([f"module load {module}" for module in selected])
        st.session_state.module_names = module_text
    else:
        st.session_state.module_names = ""


def request_version(layout):
    """Request version for modules."""
    # Get available modules only once to avoid repeated calls
    selected_modules = st.session_state.selected_modules

    for module in selected_modules:
        # Get available modules version
        module_versions = available_modules_version(module)

        # Use a dropdown to select the version
        selected_version = layout.selectbox(
            f"Select version for {module}",
            options=module_versions,
            index=0,
            key=f"version_{module}",
        )


def requirments_config(layout):
    layout.text_input(
        "Default Log File", st.session_state.selected_logs_default, key="logs_default"
    )

    layout.text_input(
        "Error Log File", st.session_state.selected_logs_error, key="logs_error"
    )

    layout.text_area(
        "Environment Commands",
        st.session_state.environment_commands,
        key="environment_commands",
    )

    # layout.text_area("Module Names", st.session_state.module_names, key="module_names")
    layout.divider()
    multi_select_modules(layout)
    request_version(layout)
    layout.divider()

    # Toggle to enable subsceduling
    layout.checkbox(
        "Enable Sub Scheduling", value=st.session_state.subsched, key="subsched"
    )

    if st.session_state.subsched:
        # If subscheduling is enabled, show the user needs to add the commnds to a list
        layout.text_area(
            "Sub Scheduling Commands",
            st.session_state.subsched_commands,
            key="subsched_commands",
        )
    else:
        layout.text_input(
            "Run Command", st.session_state.exec_command, key="exec_command"
        )
