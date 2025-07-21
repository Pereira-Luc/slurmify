# from utils.config_info import Job, System, Jobs, Resources

# Jobs = Jobs()


# # Create a custom Resources class with a typo
# class BadResources(Resources):
#     def __init__(self, account, cores, gpu, mode, nodes, time, partitions, ntasks):
#         super().__init__(account, partitions, cores, gpu, mode, nodes, time, ntasks)
#         self.partiton = partitions  # Error: Misspelled attribute name


# Jobs.add_job(
#     Job(
#         name="MisspelledAttributeJob",
#         system=System(
#             name="TypoSystem",
#             resources=BadResources(
#                 account="lxp",
#                 cores=4,
#                 gpu=None,
#                 mode="default",
#                 nodes=1,
#                 time="00:15:00",
#                 partition="cpu",
#                 ntasks=1,
#             ),
#         ),
#         exec_command="srun sleep 30",
#     )
# )


## NEEDS VALDIATION FIXING
