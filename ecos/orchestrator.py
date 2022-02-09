import random
from ecos.simulator import Simulator


class Orchestrator:
    def __init__(self, _policy):
        self.policy = _policy

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = Simulator.get_instance()

        if self.policy == "RANDOM":
            collaborationTarget = random.randrange(0, 1)

        return collaborationTarget