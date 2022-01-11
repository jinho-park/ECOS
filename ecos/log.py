from enum import Enum

class Log:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Log()

        return cls._instance

    def __init__(self):
        self.device_type = Enum("Mobile", "Edge", "Cloud")
        self.network_type = Enum("gsm", "wan", "man", "lan")
        self.file_enable = True
        self.folder_path = ""
        self.num_of_task_type = 0

        self.uncompleted_task = list()
        self.uncompleted_task_cloud = list()
        self.uncompleted_task_edge = list()
        self.uncompleted_task_mobile = list()

        self.completed_task = list()
        self.completed_task_cloud = list()
        self.completed_task_edge = list()
        self.completed_task_mobile = list()

        self.success_task = list()

        self.network_delay = list()
        self.network_delay_gsm = list()
        self.network_delay_wan = list()
        self.network_delay_man = list()
        self.network_delay_lan = list()

        self.service_time = list()
        self.service_time_cloud = list()
        self.service_time_edge = list()
        self.service_time_mobile = list()

        self.processing_time = list()
        self.processing_time_cloud = list()
        self.processing_time_edge = list()
        self.processing_time_mobile = list()

        self.buffering_time = list()
        self.buffering_time_cloud = list()
        self.buffering_time_edge = list()
        self.buffering_time_mobile = list()

    def get_service_time(self):
        return self.service_time

    def get_completed_task(self):
        return self.completed_task

    def sim_start(self, file, name):
        self.folder_path = file

    def sim_stop(self):
        if self.file_enable:
            completed_task_avg = sum(self.completed_task)
            completed_task_cloud_sum = sum(self.completed_task_cloud)
            completed_task_edge_sum = sum(self.compledted_task_edge)
            completed_task_mobile_sum = sum(self.completed_task_mobile)

            network_delay_sum = sum(self.network_delay)
            network_delay_gsm_sum = sum(self.network_delay_gsm)
            network_delay_wan_sum = sum(self.network_delay_wan)
            network_delay_man_sum = sum(self.network_delay_man)
            network_delay_lan_sum = sum(self.network_delay_lan)

            service_time_sum = sum(self.service_time)

            processing_time_sum = sum(self.processing_time)
            processing_time_cloud_sum = sum(self.processing_time_cloud)
            processing_time_edge_sum = sum(self.processing_time_edge)
            processing_time_mobile_sum = sum(self.processing_time_mobile)

            buffering_time_sum = sum(self.buffering_time)
            buffering_time_cloud_sum = sum(self.buffering_time_cloud)
            buffering_time_edge_sum = sum(self.buffering_time_edge)
            buffering_time_mobile_sum = sum(self.buffering_time_mobile)

    def task_end(self, task):
        self.record_log(task)

    def record_log(self, task):
        type = task.get_task_type()

        # processing time
        self.processing_time_cloud[type].append(task.get_processing_time(self.device_type.Cloud.value - 1))
        self.processing_time_edge[type].append(task.get_processing_time(self.device_type.Edge.value - 1))
        self.processing_time_mobile[type].append(task.get_processing_time(self.device_type.Mobile.value - 1))
        processing_time = task.get_processing_time(0) + task.get_processing_time(1) + task.get_processing_time(2)
        self.processing_time[type].append(processing_time)
        # buffering time
        self.buffering_time_cloud[type].append((task.get_buffering_time(self.device_type.Cloud.value - 1)))
        self.buffering_time_edge[type].append(task.get_buffering_time(self.device_type.Edge.value - 1))
        self.buffering_time_mobile[type].append(task.get_buffering_time(self.device_type.Mobile.value - 1))
        buffering_time = task.get_buffering_time(0) + task.get_buffering_time(1) + task.get_buffering_time(2)
        self.buffering_time[type].append(buffering_time)
        # network delay
        self.network_delay_gsm[type].append(task.get_network_delay(self.network_type.gsm.value - 1))
        self.network_delay_wan[type].append(task.get_network_delay(self.network_type.wan.value - 1))
        self.network_delay_man[type].append(task.get_network_delay(self.network_type.man.value - 1))
        self.network_delay_lan[type].append(task.get_network_delay(self.network_type.lan.value - 1))
        network_delay = task.get_network_delay(0) + task.get_network_delay(1) + \
                        task.get_network_delay(2) + task.get_network_delay(3)
        self.network_delay[type].append(network_delay)
        # service time
        service_time = processing_time + buffering_time + network_delay
        self.service_time[type].append(service_time)