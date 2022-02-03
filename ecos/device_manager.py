import random
from ecos.task_generator import Task_generator
from ecos.task import Task
from ecos.device import Device
from ecos.sim_setting import Sim_setting
from ecos.event import Event


class DeviceManager:
    def __init__(self, device_props, num_device, orchestrate=None):
        self.device_list = list()
        self.device_props = device_props
        self.num_device = num_device
        self.orchestrate_policy = orchestrate
        self.taskID = 0
        self.simSetting = Sim_setting()
        self.connectEdge = -1

        if self.orchestrate_policy is None:
            self.create_device_without_policy()
        else:
            self.create_device_with_policy()

    def create_device_with_policy(self):
        for i in range(self.num_device):
            device = Device(self.device_props[i], self.orchestrate_policy)
            self.device_list.append(device)

        self.set_connect_edge()

    def create_device_without_policy(self):
        for i in range(self.num_device):
            device = Device(i, self.device_props["mips"])
            self.device_list.append(device)

        self.set_connect_edge()

    def set_connect_edge(self):
        for i in range(self.num_device):
            randomConnectEdge = -1
            edgeSelector = random.randrange(0, 100)
            edgePercentage = 0

            for j in self.device_props[i]:
                edgePercentage += j['percentage']

                if edgeSelector <= edgePercentage:
                    randomConnectEdge = i
                    break

            if randomConnectEdge == -1:
                print("Device-Edge connection is error")
                exit(1)

    def get_offload_target(self, task):
        # if task offloading is decision in mobile device,
        # offloading policy operates in this function
        if self.connectEdge == -1:
            print("Device connection is error")
            exit(1)

        msg = {
            "type" : "task",
            "detail" : {
                "id" : 0,
                "delay" : 0,
                "dest" : self.connectEdge
            }
        }

        event = Event(msg, task)
        self.simulator.send_event(event)

    def create_task(self, edge_prop):
        task = Task(edge_prop, ++self.taskID)

        return task