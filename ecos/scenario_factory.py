from abc import *


class Scenario_factory(metaclass=ABCMeta):
    @abstractmethod
    def get_device_manager(self):
        pass

    @abstractmethod
    def get_edge_manager(self):
        pass

    @abstractmethod
    def get_cloud_manager(self):
        pass
