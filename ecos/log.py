import json
from enum import Enum

class Log:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Log()

        return cls._instance

    def __init__(self):
        # 0: Mobile, 1: Edge, 2: Cloud
        self.device_type = 0
        # lan: mobile-edge, man: edge-edge, wan: edge-cloud
        # 0: gsm, 1: wan, 2: man, 3: lan
        self.network_type = 0
        self.file_enable = True
        self.file_name = ""
        self.folder_path = ""
        self.num_of_task_type = 0

        self.completed_task = 0
        self.completed_task_cloud = 0
        self.completed_task_edge = 0
        self.completed_task_mobile = 0

        self.success_task = 0

        self.network_delay = list()
        self.network_delay_gsm = list()
        self.network_delay_wan = list()
        self.network_delay_man = list()
        self.network_delay_lan = list()

        self.service_time = list()

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
        self.file_name = name

    def sim_stop(self):
        if self.file_enable:
            completed_task_sum = self.completed_task
            completed_task_cloud_sum = self.completed_task_cloud
            completed_task_edge_sum = self.completed_task_edge
            completed_task_mobile_sum = self.completed_task_mobile

            network_delay_avg = sum(self.network_delay) / len(self.network_delay)
            network_delay_gsm_avg = sum(self.network_delay_gsm) / len(self.network_delay_gsm)
            network_delay_wan_avg = sum(self.network_delay_wan) / len(self.network_delay_wan)
            network_delay_man_avg = sum(self.network_delay_man) / len(self.network_delay_man)
            network_delay_lan_avg = sum(self.network_delay_lan) / len(self.network_delay_lan)

            service_time_avg = sum(self.service_time) / len(self.service_time)

            processing_time_avg = sum(self.processing_time) / len(self.processing_time)
            processing_time_cloud_avg = sum(self.processing_time_cloud) / len(self.processing_time_cloud)
            processing_time_edge_avg = sum(self.processing_time_edge) / len(self.processing_time_edge)
            processing_time_mobile_avg = sum(self.processing_time_mobile) / len(self.processing_time_mobile)

            buffering_time_avg = sum(self.buffering_time) / len(self.buffering_time)
            buffering_time_cloud_avg = sum(self.buffering_time_cloud) / len(self.buffering_time_cloud)
            buffering_time_edge_avg = sum(self.buffering_time_edge) / len(self.buffering_time_edge)
            buffering_time_mobile_avg = sum(self.buffering_time_mobile) / len(self.buffering_time_mobile)

            result = {
                "completed_task": {
                    "total_completed_task": completed_task_sum,
                    "completed_task_cloud" : completed_task_cloud_sum,
                    "completed_task_edge": completed_task_edge_sum,
                    "completed_task_mobile": completed_task_mobile_sum
                },
                "service_time" : service_time_avg,
                "processing_delay": {
                    "processing_time" : processing_time_avg,
                    "processing_time_cloud_avg": processing_time_cloud_avg,
                    "processing_time_edge_avg": processing_time_edge_avg,
                    "processing_time_mobile_avg": processing_time_mobile_avg
                },
                "network_delay": {
                    "network_time": network_delay_avg,
                    "network_delay_gsm": network_delay_gsm_avg,
                    "network_delay_wan": network_delay_wan_avg,
                    "network_delay_man": network_delay_man_avg,
                    "network_delay_lan": network_delay_lan_avg,
                },
                "buffering_delay": {
                    "buffering_time": buffering_time_avg,
                    "buffering_time_cloud": buffering_time_cloud_avg,
                    "buffering_time_edge": buffering_time_edge_avg,
                    "buffering_time_mobile": buffering_time_mobile_avg
                }
            }

        with open(self.file_name, 'w', encoding="utf-8") as make_file:
            json.dump(result, make_file, ensure_ascii=False, indent="\n")

    def task_end(self, task):
        self.record_log(task)

    def record_log(self, task):
        type = task.get_task_type()

        # processing time
        self.processing_time_cloud[type].append(task.get_processing_time(2))
        self.processing_time_edge[type].append(task.get_processing_time(1))
        self.processing_time_mobile[type].append(task.get_processing_time(0))
        processing_time = task.get_processing_time(0) + task.get_processing_time(1) + task.get_processing_time(2)
        self.processing_time[type].append(processing_time)

        # buffering time
        self.buffering_time_cloud[type].append((task.get_buffering_time(2)))
        self.buffering_time_edge[type].append(task.get_buffering_time(1))
        self.buffering_time_mobile[type].append(task.get_buffering_time(0))
        buffering_time = task.get_buffering_time(0) + task.get_buffering_time(1) + task.get_buffering_time(2)
        self.buffering_time[type].append(buffering_time)

        # network delay
        self.network_delay_gsm[type].append(task.get_network_delay(0))
        self.network_delay_wan[type].append(task.get_network_delay(1))
        self.network_delay_man[type].append(task.get_network_delay(2))
        self.network_delay_lan[type].append(task.get_network_delay(3))
        network_delay = task.get_network_delay(0) + task.get_network_delay(1) + \
                        task.get_network_delay(2) + task.get_network_delay(3)
        self.network_delay[type].append(network_delay)

        # service time
        service_time = processing_time + buffering_time + network_delay
        self.service_time[type].append(service_time)

        if task.get_task_deadline() > service_time:
            self.completed_task += 1

            if task.get_finish_node() == 0:
                self.completed_task_mobile += 1
            elif task.get_finish_node() == 1:
                self.completed_task_edge += 1
            elif task.get_finish_node() == 2:
                self.completed_task_cloud += 1