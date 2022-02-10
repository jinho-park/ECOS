from ecos.simulator import Simulator
import random


class Orchestrator:
    def __init__(self, _policy):
        self.policy = _policy

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = Simulator.get_instance()

        if self.policy == "RANDOM":
            Cloudid = simul.scenario_factory.get_cloud_manager().get_cloud_id()
            edgeidlist = [Cloudid]
            for i in range(simul.scenario_factory.get_edge_manager().get_node_list()):
                edgeidlist.append(i+1)

            selectServer = random.choice(edgeidlist)
            collaborationTarget = selectServer

        return collaborationTarget