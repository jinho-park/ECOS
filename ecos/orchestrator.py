from ecos.simulator import Simulator
import random


class Orchestrator:
    def __init__(self, _policy):
        self.policy = _policy

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = Simulator.get_instance()

        if self.policy == "RANDOM":
            num_of_edge = simul.get_num_of_edge()
            selectServer = random.randrange(0, num_of_edge + 1)
            collaborationTarget = selectServer

        return collaborationTarget
