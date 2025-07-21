import token
import streamlit as st
import datetime
import time

from streamlit_functions.func import cancel_job, get_node_info


def format_timestamp(timestamp):
    """Convert Unix timestamp to readable datetime format"""
    if timestamp and timestamp.get("set") and timestamp["number"] > 0:
        return datetime.datetime.fromtimestamp(timestamp["number"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    return "N/A"


def calculate_runtime(start, end=None):
    """Calculate runtime between timestamps"""
    if not start or not start.get("set") or start["number"] <= 0:
        return "N/A"

    start_time = start["number"]
    end_time = (
        end["number"] if end and end.get("set") and end["number"] > 0 else time.time()
    )

    seconds = int(end_time - start_time)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_job_status(job_data):
    """Get job status from job data"""
    if not job_data or "jobs" not in job_data or not job_data["jobs"]:
        return None

    job = job_data["jobs"][0]

    # Extract relevant information
    job_status = {
        "job_id": job.get("job_id", "N/A"),
        "job_state": ", ".join(job.get("job_state", ["Unknown"])),
        "partition": job.get("partition", "N/A"),
        "qos": job.get("qos", "N/A"),
        "start_time": format_timestamp(job.get("start_time")),
        "end_time": format_timestamp(job.get("end_time")),
        "submit_time": format_timestamp(job.get("submit_time")),
    }

    return job_status


def display_job_status(job_data):
    if not job_data or "jobs" not in job_data or not job_data["jobs"]:
        st.warning("No job information available")
        return

    job = job_data["jobs"][0]

    # Create three columns for key info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Job ID", job.get("job_id", "N/A"))
        st.metric("Status", ", ".join(job.get("job_state", ["Unknown"])))

    with col2:
        st.metric("Queue", job.get("partition", "N/A"))
        st.metric("QoS", job.get("qos", "N/A"))

    with col3:
        runtime = calculate_runtime(
            job.get("start_time"),
            job.get("end_time") if "RUNNING" not in job.get("job_state", []) else None,
        )
        st.metric("Runtime", runtime)

        # Calculate remaining time if time limit exists
        time_limit_mins = (
            job.get("time_limit", {}).get("number", 0) * 60
            if job.get("time_limit")
            else 0
        )
        if time_limit_mins > 0 and "RUNNING" in job.get("job_state", []):
            elapsed_seconds = time.time() - job.get("start_time", {}).get(
                "number", time.time()
            )
            remaining_seconds = max(0, (time_limit_mins * 60) - elapsed_seconds)
            remaining_mins = int(remaining_seconds / 60)
            st.metric("Remaining Time", f"{remaining_mins} mins")

    # Expandable section with detailed info
    with st.expander("Detailed Information"):
        detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(
            ["Resources", "Timing", "Files", "Nodes"]
        )

        with detail_tab1:
            st.metric("Nodes", job.get("nodes", "N/A"))
            st.metric("CPUs", str(job.get("cpus", {}).get("number", "N/A")))
            st.metric(
                "Memory", f"{job.get('memory_per_cpu', {}).get('number', 0)} MB per CPU"
            )

            # Resources utilization info if available
            if job.get("job_resources", {}).get("allocated_nodes"):
                node_info = job["job_resources"]["allocated_nodes"][0]
                st.metric(
                    "CPU Usage",
                    f"{node_info.get('cpus_used', 0)}/{job.get('cpus', {}).get('number', 0)}",
                )

        with detail_tab2:
            st.metric("Submit Time", format_timestamp(job.get("submit_time")))
            st.metric("Start Time", format_timestamp(job.get("start_time")))
            st.metric("Expected End", format_timestamp(job.get("end_time")))

        with detail_tab3:
            st.text("Standard Output")
            st.code(job.get("standard_output", "N/A"), language="bash")

            st.text("Standard Error")
            st.code(job.get("standard_error", "N/A"), language="bash")

            st.text("Working Directory")
            st.code(job.get("current_working_directory", "N/A"), language="bash")

        # New tab for node details
        with detail_tab4:
            # Check if job has allocated nodes
            if "RUNNING" in job.get("job_state", []) and job.get(
                "job_resources", {}
            ).get("allocated_nodes"):
                allocated_nodes = job["job_resources"]["allocated_nodes"]

                for node in allocated_nodes:
                    node_name = node.get("nodename", "unknown-node")
                    st.subheader(f"Node: {node_name}")

                    # Get detailed node info if JWT token is in session state
                    if "selected_JWT_token" in st.session_state:
                        with st.spinner(f"Fetching details for node {node_name}..."):
                            print("Fetching node details..." + node_name)
                            node_detail = get_node_info(
                                st.session_state.selected_JWT_token, node_name
                            )

                            if (
                                node_detail
                                and "nodes" in node_detail
                                and node_detail["nodes"]
                            ):
                                node_data = node_detail["nodes"][0]

                                # Display node metrics in columns for better organization
                                node_col1, node_col2, node_col3 = st.columns(3)

                                with node_col1:
                                    st.metric(
                                        "CPU Load",
                                        f"{node_data.get('cpu_load', 'N/A')}",
                                    )
                                    st.metric(
                                        "CPUs Total", node_data.get("cpus", "N/A")
                                    )
                                    st.metric(
                                        "CPUs Allocated",
                                        node_data.get("alloc_cpus", "N/A"),
                                    )

                                with node_col2:
                                    ram_total = node_data.get("real_memory", 0)
                                    ram_alloc = node_data.get("alloc_memory", 0)
                                    free_mem = node_data.get("free_mem", {}).get(
                                        "number", 0
                                    )

                                    st.metric("RAM Total (MB)", ram_total)
                                    st.metric("RAM Allocated (MB)", ram_alloc)
                                    st.metric("RAM Free (MB)", free_mem)

                                with node_col3:
                                    st.metric(
                                        "Architecture",
                                        node_data.get("architecture", "N/A"),
                                    )
                                    st.metric(
                                        "State",
                                        ", ".join(node_data.get("state", ["Unknown"])),
                                    )
                            else:
                                st.warning(
                                    f"Could not fetch detailed information for node {node_name}"
                                )
                    else:
                        st.warning(
                            "JWT token not available. Cannot fetch node details."
                        )
            else:
                st.info("No allocated nodes information available for this job")
