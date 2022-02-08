from ecos.simulator import Simulator


class Orchestrator:
    def __init__(self, _policy):
        self.simulation = Simulator.get_instance()
        self.policy = _policy

    def offloading_target(self, task):
        collaborationTarget = 0
        location = self.simulation.get_mobility.get_location(self.simulation.get_clock(), task)

        if self.policy == "RANDOM":
            print("1")
            collaborationTarget = 1


        return collaborationTarget