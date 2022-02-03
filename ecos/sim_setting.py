import json
from enum import Enum


# 22.01.05
class Sim_setting:
    _instance = None

    # singleton
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Sim_setting()
        return cls._instance

    def __init__(self):
        self.nodeId = {
            "Mobile" : 1,
            "Edge": 2,
            "Cloud" : 3
        }

        # WLAN : device-edge, MAN : edge-edge, WAN : edge-cloud
        self.networkType = {
            "WLAN" : 1,
            "MAN" : 2,
            "WAN" : 3
        }
        self.simulationTime = 0
        self.warmUpPeriod = 0
        self.intervalToGetLoadLog = 0
        self.fileLogEnable = True

        self.minNumOfMobileDevice = 0
        self.maxNumOfMobileDevice = 0
        self.mobileDeviceCounterSize = 0
        self.numOfEdge = 0

        self.wlanPropagationDelay = 0
        self.manPropagationDelay = 0
        self.wanPropagationDelay = 0
        self.wlanBandwidth = 0
        self.manBandwidth = 0
        self.wanBandwidth = 0

        self.simulationScenario = list()
        self.collaborationScenario = list()

        #
        self.taskLookUpTable = list()

    def get_simulation_time(self):
        return self.simulationTime

    def get_warmup_period(self):
        return self.warmUpPeriod

    def get_load_log_interval(self):
        return self.intervalToGetLoadLog

    def get_file_log_enable(self):
        return self.fileLogEnable

    def get_wlan_propagation_delay(self):
        return self.wlanPropagationDelay

    def get_man_propagation_delay(self):
        return self.manPropagationDelay

    def get_wan_propagation_delay(self):
        return self.wanPropagationDelay

    def get_wlan_bandwidth(self):
        return self.wlanBandwidth

    def get_man_bandwidth(self):
        return self.manBandwidth

    def get_wan_bandwidth(self):
        return self.wanBandwidth

    def get_min_num_of_mobiledevice(self):
        return self.minNumOfMobileDevice

    def get_max_num_of_mobiledevice(self):
        return self.maxNumOfMobileDevice

    def get_num_of_edge(self):
        return self.numOfEdge

    def get_scenario(self):
        return self.simulationScenario

    def get_collaboration_scenario(self):
        return self.collaborationScenario

    def get_task_look_up_table(self):
        return self.taskLookUpTable

    def get_task_properties(self, taskType):
        result = self.taskLookUpTable[taskType-1]

        return result

    def parse_json_file(self, file):
        json_file = json.dumps(file, indent=4)

        return json_file