import streamlit as st
from utils.config_getters import (
    calculate_max_gpus,
    get_max_cpus_partition,
    get_valid_partitions,
    get_valid_modes,
    get_max_time_for_mode,
    calculate_max_nodes,
)
import datetime


def resource_config_prompt(layout):
    partitions: list[str] = get_valid_partitions()

    layout.segmented_control(
        "Partitions",
        partitions,
        selection_mode="single",
        default=st.session_state.selected_partion,
        key="selected_partion",
    )

    qos = get_valid_modes()

    layout.segmented_control(
        "Select the QOS",
        qos,
        selection_mode="single",
        default=st.session_state.selected_qos,
        key="selected_qos",
    )

    max_nodes: int | None = calculate_max_nodes(
        partition=st.session_state.selected_partion, mode=st.session_state.selected_qos
    )

    layout.number_input(
        "Select the amount of nodes",
        min_value=1,
        max_value=max_nodes if max_nodes else 1,
        value=(
            st.session_state.selected_nodes
            if max_nodes > st.session_state.selected_nodes
            else 1
        ),
        key="selected_nodes",
    )

    layout.number_input(
        "Select the amount of ntasks",
        min_value=st.session_state.selected_nodes,
        value=(
            st.session_state.selected_ntasks
            if st.session_state.selected_ntasks > st.session_state.selected_nodes
            else st.session_state.selected_nodes
        ),
        step=1,
        key="selected_ntasks",
    )

    max_amount_of_cpus: int = get_max_cpus_partition(st.session_state.selected_partion)
    layout.number_input(
        "Select the amount of CPUs",
        min_value=1,
        max_value=max_amount_of_cpus,
        value=(st.session_state.selected_cpus % (max_amount_of_cpus + 1)),
        key="selected_cpus",
    )

    if st.session_state.selected_partion == "gpu":
        max_gpus = calculate_max_gpus(mode=st.session_state.selected_qos)
        layout.number_input(
            "Select the amount of GPUs",
            min_value=1,
            max_value=max_gpus,
            key="selected_gpus",
        )
    else:
        # Reset GPU to 0 when not using GPU partition
        st.session_state.selected_gpus = 0

    max_time_str = get_max_time_for_mode(mode=st.session_state.selected_qos)
    HH, MM, SS = map(int, max_time_str.strip().split(":"))
    total_hours = HH + (1 if MM > 0 or SS > 0 else 0)

    # Default value: 1 hour
    default_hours = min(1, total_hours)

    # Slider in hours
    selected_hours = layout.slider(
        "Wall Time (in hours)",
        min_value=1,
        max_value=total_hours,
        value=default_hours,
        step=1,
        key="wall_time_hours",
    )

    # Format as HH:MM:SS (always with 00:00)
    wall_time_str = f"{selected_hours:02}:00:00"
    st.session_state.wall_time_str = wall_time_str
    st.session_state.wall_time_str = wall_time_str
    layout.divider()
