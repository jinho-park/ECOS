import random
from ecos.task import Task
from ecos.device import Device
from ecos.event import Event
from ecos.simulator import Simulator


class DeviceManager:
    def __init__(self, device_props, num_device, edge_props, orchestrate=None):
        self.device_list = list()
        self.device_props = device_props
        self.edge_props = edge_props
        self.num_device = num_device
        self.orchestrate_policy = orchestrate
        self.taskID = 0
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1

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

    def get_state(self):
        return self.state

    def start_entity(self):
        if self.state == 1:
            self.state = 2

        return True

    def shutdown_entity(self):
        if self.state == 2:
            self.state = 1

        return True

    def set_connect_edge(self):
        for device in self.device_list:
            randomConnectEdge = -1
            edgeSelector = random.randrange(0, 100)
            edgePercentage = 0

            for j in range(len(self.edge_props)):
                edgePercentage += int(self.edge_props[j]['percentage'])

                if edgeSelector <= edgePercentage:
                    randomConnectEdge = j
                    device.set_connected_edge(randomConnectEdge)
                    break

            if randomConnectEdge == -1:
                print("Device-Edge connection is error")
                exit(1)

    def get_offload_target(self, task):
        # if task offloading is decision in mobile device,
        # offloading policy operates in this function
        sending_target = random.randrange(1, Simulator.get_instance().get_num_of_edge())
        if sending_target == -1:
            print("Device connection is error")
            exit(1)

        msg = {
            "task" : "processing",
            "detail" : {
                "id" : 0,
                "delay" : 0,
                "source" : -1,
                "dest" : sending_target
            }
        }

        event = Event(msg, task, 0)
        Simulator.get_instance().send_event(event)

    def create_task(self, edge_prop):
        task = Task(edge_prop, ++self.taskID)

        return task