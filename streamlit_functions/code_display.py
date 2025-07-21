from streamlit_functions.func import get_slurm


def display_code(layout):
    slurm, job = get_slurm(layout)
    layout.code(body=slurm, language="bash")

    return slurm, job
