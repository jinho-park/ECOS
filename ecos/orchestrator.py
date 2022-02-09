import random
from ecos.simulator import Simulator
from ecos.edge_manager import EdgeManager
from ecos.cloud_manager import CloudManager
import random


class Orchestrator:
    def __init__(self, _policy):
        self.policy = _policy

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = Simulator.get_instance()

        if self.policy == "RANDOM":
            Selectserver = random.choice(CloudManager.get_cloud_id(), EdgeManager.get_edge_id())
            if Selectserver == CloudManager.get_cloud_id() :
                collaborationTarget = CloudManager.get_cloud_id()

            elif Selectserver == EdgeManager.get_edge_id() :
                Selectedge = random.choice(EdgeManager.get_edge_list())
                collaborationTarget = Selectedge

        return collaborationTarget