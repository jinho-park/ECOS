import json
import numpy as np


class Log:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Log()

        return cls._instance

    def __init__(self):
        # 2: Mobile, 1: Edge, 0: Cloud
        self.device_type = {
            "mobile": 2,
            "edge": 1,
            "cloud": 0
        }
        # lan: mobile-edge, man: edge-edge, wan: edge-cloud
        # 0: gsm, 1: wan, 2: man, 3: lan
        self.network_type = {
            "lan": 1,
            "man": 2,
            "wan": 3
        }
        self.file_enable = True
        self.file_name = ""
        self.folder_path = ""
        self.num_of_task_type = 0
        self.num_of_edge = 0
        self.warmup_time = 0

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
        self.service_time_list = list()

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

    def sim_start(self, name, num_of_edge, warmup):
        self.__init__()
        # self.folder_path = file
        self.file_name = name
        self.num_of_edge = num_of_edge
        self.warmup_time = warmup

        for i in range(num_of_edge):
            self.service_time_list.append(list())

    def sim_stop(self):
        if self.file_enable:
            completed_task_sum = self.completed_task
            completed_task_cloud_sum = self.completed_task_cloud
            completed_task_edge_sum = self.completed_task_edge
            completed_task_mobile_sum = self.completed_task_mobile
            edge_service_time_list = []

            network_delay_avg = np.divide(sum(self.network_delay), len(self.network_delay),
                                          out=np.zeros_like(sum(self.network_delay)),
                                          where=len(self.network_delay) != 0,
                                          casting="unsafe")
            network_delay_gsm_avg = np.divide(sum(self.network_delay_gsm), len(self.network_delay_gsm),
                                              out=np.zeros_like(sum(self.network_delay_gsm)),
                                              where=len(self.network_delay_gsm),
                                              casting="unsafe")
            network_delay_wan_avg = np.divide(sum(self.network_delay_wan), len(self.network_delay_wan),
                                              out=np.zeros_like(sum(self.network_delay_wan)),
                                              where=len(self.network_delay_wan),  casting="unsafe")
            network_delay_man_avg = np.divide(sum(self.network_delay_man), len(self.network_delay_man),
                                              out=np.zeros_like(sum(self.network_delay_man)),
                                              where=len(self.network_delay_man),  casting="unsafe")
            network_delay_lan_avg = np.divide(sum(self.network_delay_lan), len(self.network_delay_lan),
                                              out=np.zeros_like(sum(self.network_delay_lan)),
                                              where=len(self.network_delay_lan),  casting="unsafe")

            service_time_avg = np.divide(sum(self.service_time), len(self.service_time),
                                         out=np.zeros_like(sum(self.service_time)),
                                         where=len(self.service_time), casting="unsafe")

            for service_time in self.service_time_list:
                s_time = np.divide(sum(service_time), len(service_time),
                                   out=np.zeros_like(sum(service_time)),
                                   where=len(service_time), casting="unsafe")
                edge_service_time_list.append(s_time.tolist())

            processing_time_avg = np.divide(sum(self.processing_time), len(self.processing_time),
                                            out=np.zeros_like(sum(self.processing_time)),
                                            where=len(self.processing_time), casting="unsafe")
            processing_time_cloud_avg = np.divide(sum(self.processing_time_cloud), len(self.processing_time_cloud),
                                                  out=np.zeros_like(sum(self.processing_time_cloud)),
                                                  where=len(self.processing_time_cloud), casting="unsafe")
            processing_time_edge_avg = np.divide(sum(self.processing_time_edge), len(self.processing_time_edge),
                                                 out=np.zeros_like(sum(self.processing_time_edge)),
                                                 where=len(self.processing_time_edge), casting="unsafe")
            processing_time_mobile_avg = np.divide(sum(self.processing_time_mobile), len(self.processing_time_mobile),
                                                   out=np.zeros_like(sum(self.processing_time_mobile)),
                                                   where=len(self.processing_time_mobile), casting="unsafe")

            buffering_time_avg = np.divide(sum(self.buffering_time), len(self.buffering_time),
                                           out=np.zeros_like(sum(self.buffering_time)),
                                           where=len(self.buffering_time), casting="unsafe")
            buffering_time_cloud_avg = np.divide(sum(self.buffering_time_cloud), len(self.buffering_time_cloud),
                                                 out=np.zeros_like(sum(self.buffering_time_cloud)),
                                                 where=len(self.buffering_time_cloud), casting="unsafe")
            buffering_time_edge_avg = np.divide(sum(self.buffering_time_edge), len(self.buffering_time_edge),
                                                out=np.zeros_like(sum(self.buffering_time_edge)),
                                                where=len(self.buffering_time_edge), casting="unsafe")
            buffering_time_mobile_avg = np.divide(sum(self.buffering_time_mobile), len(self.buffering_time_mobile),
                                                  out=np.zeros_like(sum(self.buffering_time_mobile)),
                                                  where=len(self.buffering_time_mobile), casting="unsafe")

            result = {
                "completed_task": {
                    "total_completed_task": completed_task_sum,
                    "completed_task_cloud" : completed_task_cloud_sum,
                    "completed_task_edge": completed_task_edge_sum,
                    "completed_task_mobile": completed_task_mobile_sum
                },
                "success_task": self.success_task,
                "service_time" : service_time_avg.tolist(),
                "service_time_edge" : edge_service_time_list,
                "processing_delay": {
                    "processing_time" : processing_time_avg.tolist(),
                    "processing_time_cloud_avg": processing_time_cloud_avg.tolist(),
                    "processing_time_edge_avg": processing_time_edge_avg.tolist(),
                    "processing_time_mobile_avg": processing_time_mobile_avg.tolist()
                },
                "network_delay": {
                    "network_time": network_delay_avg.tolist(),
                    "network_delay_gsm": network_delay_gsm_avg.tolist(),
                    "network_delay_wan": network_delay_wan_avg.tolist(),
                    "network_delay_man": network_delay_man_avg.tolist(),
                    "network_delay_lan": network_delay_lan_avg.tolist(),
                },
                "buffering_delay": {
                    "buffering_time": buffering_time_avg.tolist(),
                    "buffering_time_cloud": buffering_time_cloud_avg.tolist(),
                    "buffering_time_edge": buffering_time_edge_avg.tolist(),
                    "buffering_time_mobile": buffering_time_mobile_avg.tolist()
                }
            }

            with open(self.file_name, 'w', encoding="utf-8") as make_file:
                json.dump(result, make_file, ensure_ascii=False, indent='\n')

    def task_end(self, task):
        self.record_log(task)

    def record_log(self, task):
        # type = task.get_task_type()
        if task.get_birth_time() < self.warmup_time:
            return

        # processing time
        self.processing_time_cloud.append(task.get_processing_time(self.device_type["cloud"]))
        self.processing_time_edge.append(task.get_processing_time(self.device_type["edge"]))
        self.processing_time_mobile.append(task.get_processing_time(self.device_type["mobile"]))
        processing_time = task.get_processing_time_sum()
        self.processing_time.append(processing_time)

        # buffering time
        self.buffering_time_cloud.append((task.get_buffering_time(self.device_type["cloud"])))
        self.buffering_time_edge.append(task.get_buffering_time(self.device_type["edge"]))
        self.buffering_time_mobile.append(task.get_buffering_time(self.device_type["mobile"]))
        buffering_time = task.get_buffering_time_sum()
        self.buffering_time.append(buffering_time)

        # network delay
        self.network_delay_gsm.append(task.get_network_delay(0))
        self.network_delay_wan.append(task.get_network_delay(1))
        self.network_delay_man.append(task.get_network_delay(2))
        self.network_delay_lan.append(task.get_network_delay(3))
        network_delay = task.get_network_delay(0) + task.get_network_delay(1) + \
                        task.get_network_delay(2) + task.get_network_delay(3)
        self.network_delay.append(network_delay)

        # service time
        service_time = processing_time + buffering_time + network_delay
        self.service_time.append(service_time)
        edge_num = task.get_source_node()
        self.service_time_list[edge_num - 1].append(service_time)

        self.completed_task += 1

        if task.get_finish_node() == 0:
            self.completed_task_mobile += 1
        elif task.get_finish_node() == 1:
            self.completed_task_edge += 1
        elif task.get_finish_node() == 2:
            self.completed_task_cloud += 1

        if (task.get_task_deadline() / 1000) > service_time:
            self.success_task += 1
