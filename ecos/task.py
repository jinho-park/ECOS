import time


# 21.11.17
class Task:
    def __init__(self, task_prop, id):
        self.task_type = task_prop["type"]
        self.task_size = task_prop["inputSize"]
        self.id = id
        self.task_input_size = task_prop["inputSize"]
        self.task_output_size = task_prop["outputSize"]
        self.task_deadline = task_prop["deadline"]
        self.task_remain_size = 0
        self.task_birth_time = 0
        self.task_receive_time = 0
        self.task_start_time = 0
        self.task_end_time = 0
        # 0 = mobile, 1 = edge, 2 = cloud
        self.buffering_time = [0, 0, 0]
        self.processing_time = [0, 0, 0]
        # lan: mobile-edge, man: edge-edge, wan: edge-cloud
        # 0= gsm, 1=wan, 2=man, 3=lan
        self.network_delay = [0, 0, 0, 0]
        self.finish_node = 0
        self.allocated_resource = 0
        self.source_node = -1
        self.processing_node = -1
        # 0: create, 1: transmission, 2: processing
        self.status = 0

        self.load_balance = 0

    def create_task(self, _time):
        self.task_birth_time = _time
        self.task_remain_size = self.task_size

    def get_task_type(self):
        return self.task_type

    def get_remain_size(self):
        return self.task_remain_size

    def get_input_size(self):
        return self.task_input_size

    def get_birth_time(self):
        return self.task_birth_time

    def get_receive_time(self):
        return self.task_receive_time

    def get_start_time(self):
        return self.task_start_time

    def get_end_time(self):
        return self.task_end_time

    def set_remain_size(self, size):
        self.task_remain_size = size

    def set_receive_time(self):
        self.task_receive_time = time.time()

    def set_start_time(self, _time):
        self.task_start_time = _time

    def set_end_time(self, _time):
        self.task_end_time = _time

    def update_finish_time(self, _time):
        self.task_end_time = _time

    def set_buffering_time(self, buff, type):
        self.buffering_time[type] = buff - sum(self.network_delay) - self.task_birth_time

        if self.buffering_time[type] < 0:
            print("buffering time error", self.buffering_time[type])

    def set_processing_time(self, proc, type):
        net_delay = sum(self.network_delay)
        buff_delay = sum(self.buffering_time)
        self.processing_time[type] = proc - net_delay - buff_delay - self.task_birth_time

        if self.processing_time[type] < 0:
            print("processing time error", self.processing_time[type])

    def set_network_delay(self, value, type):
        self.network_delay[type] = value - self.task_birth_time

        if self.network_delay[type] < 0:
            print("network delay error", self.network_delay[type])

    def get_buffering_time(self, type):
        return self.buffering_time[type]

    def get_buffering_time_sum(self):
        return sum(self.buffering_time)

    def get_processing_time(self, type):
        return self.processing_time[type]

    def get_processing_time_sum(self):
        return sum(self.processing_time)

    def get_network_delay(self, type):
        return self.network_delay[type]

    def get_network_delay_sum(self):
        return sum(self.network_delay)

    def get_task_deadline(self):
        return self.task_deadline

    def set_finish_node(self, type):
        self.finish_node = type

    def get_finish_node(self):
        return self.finish_node

    def set_allocated_resource(self, resource):
        self.allocated_resource = resource

    def get_allocated_resource(self):
        return self.allocated_resource

    def set_processing_node(self, node_id):
        self.processing_node = node_id

    def set_source_node(self, node_id):
        self.source_node = node_id

    def get_source_node(self):
        return self.source_node

    def set_status(self, status):
        self.status = status

    def set_load_balance(self, load_balance):
        self.load_balance = load_balance
