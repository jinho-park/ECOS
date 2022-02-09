class Device:
    def __init__(self, id, mips):
        self.deviceId = id
        self.MIPS = mips
        self.avail_MIPS = self.MIPS
        self.processing_task_list = list()
        self.buffered_task_list = list()
        self.connected_edge_id = -1

    def set_connected_edge(self, edge_id):
        self.connected_edge_id = edge_id

    def get_connected_edge(self):
        return self.connected_edge_id
