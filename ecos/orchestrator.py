from ecos.simulator import Simulator
from ecos.edge_manager import EdgeManager
from ecos.cloud_manager import CloudManager
import random


class Orchestrator:
    def __init__(self, _policy):
        self.simulation = Simulator.get_instance()
        self.policy = _policy


    def offloading_target(self, task):
        collaborationTarget = 0
        location = self.simulation.get_mobility.get_location(self.simulation.get_clock(), task)

        if self.policy == "RANDOM":
            Selectserver = random.choice(CloudManager.get_cloud_id(), EdgeManager.get_edge_id())
            if Selectserver == CloudManager.get_cloud_id() :
                collaborationTarget = CloudManager.get_cloud_id()

            elif Selectserver == EdgeManager.get_edge_id() :
                Selectedge = random.choice(EdgeManager.get_edge_list())
                collaborationTarget = Selectedge


        return collaborationTarget