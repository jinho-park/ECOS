class Device:
    def __init__(self, id, device_props, orchestrate_policy):
        self.deviceId = id
        self.MIPS = device_props["MIPS"]
        self.avail_MIPS = self.MIPS
        self.orchestrate = orchestrate_policy
        self.processing_task_list = list()
        self.buffered_task_list = list()
