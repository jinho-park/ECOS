class Device:
    def __init__(self, id, mips):
        self.deviceId = id
        self.MIPS = mips
        self.avail_MIPS = self.MIPS
        self.processing_task_list = list()
        self.buffered_task_list = list()
