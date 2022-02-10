class Device:
    def __init__(self, id, mips):
        self.deviceId = id
        self.MIPS = mips
        self.avail_MIPS = self.MIPS
        self.processing_task_list = list()
        self.buffered_task_list = list()
        self.connected_edge_id = -1
        self.previousTime = 0

    def set_connected_edge(self, edge_id):
        self.connected_edge_id = edge_id

    def get_connected_edge(self):
        return self.connected_edge_id

    def update_task_state(self, simulationTime):
        timeSpen = simulationTime - self.previousTime

        for task in self.processing_task_list:
            task.update_finish_time((timeSpen))

        if len(self.processing_task_list) == 0 and len(self.buffered_task_list) == 0:
            self.previousTime = simulationTime
