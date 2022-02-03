import simpy

from ecos.topology import Topology
from ecos.device_manager import DeviceManager

#21.11.7
class Simulation:
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls.get_instance()
        return cls._instance

    def __init__(self,
                 simulation_time_end,
                 edge_manager,
                 cloud_manager,
                 device_mobility,
                 task_generator,
                 device_manager,
                 topology=Topology()):
        self.env = simpy.Environment()
        self.ev_buf = list()
        self.stop = False

        self.topology = topology
        self.device_manager = device_manager
        self.edge_manager = edge_manager
        self.cloud_manager = cloud_manager
        self.task_generator = task_generator
        self.device_mobility = device_mobility
        self.Logger = ''
        # this simulation processing the event according to millisecond unit
        self.simulation_time_now = 0
        self.simulation_time_end = simulation_time_end
        # sequential event processing
        self.event_list = list()

    def get_topology(self):
        return self.topology

    def get_device_manager(self):
        return self.device_manager

    def get_edge_manager(self):
        return self.edge_manager

    def get_cloud_manager(self):
        return self.cloud_manager

    def get_task_manager(self):
        return self.task_generator

    def get_device_mobility(self):
        return self.device_mobility

    def run(self):
        while not self.stop:
            event = self.event_list[0]

            if event.time < 1:
                # call function

                self.simulation_time_now = event.time
            else:
                self.simulation_time_now += 1

            if self.simulation_time_now >= self.simulation_time_end:
                self.Logger
                return

