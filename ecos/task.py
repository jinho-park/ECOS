import time

# 21.11.17
class Task:
    def __init__(self, task_prop, id):
        self.task_type = task_prop["type"]
        self.task_size = task_prop["size"]
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
        # 0= gsm, 1=wan, 2=man, 3=lan
        self.network_delay = [0, 0, 0, 0]

    def create_task(self):
        self.task_birth_time = time.time()
        self.task_remain_size = self.task_size

    def get_task_type(self):
        return self.task_type

    def get_remain_size(self):
        return self.task_remain_size

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

    def set_start_time(self):
        self.task_start_time = time.time()

    def set_end_time(self):
        self.task_start_time = time.time()

    def update_finish_time(self, _time):
        self.task_end_time = _time

    def set_buffering_time(self, buff, type):
        self.buffering_time[type] = buff

    def set_processing_time(self, proc, type):
        self.processing_time[type] = proc

    def set_network_delay(self, value, type):
        self.network_delay[type] = value

    def get_buffering_time(self, type):
        return self.buffering_time[type]

    def get_processing_time(self, type):
        return self.processing_time[type]

    def get_network_delay(self, type):
        return self.network_delay[type]
