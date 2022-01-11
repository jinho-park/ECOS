from simulator import Simulator
from sim_setting import Sim_setting

class Orchestrator:
    def __init__(self, _policy):
        self.simulation = Simulator.get_instance()
        self.sim_setting = Sim_setting.get_instance()
        self.policy = _policy

    def offloaindg_target(self, task):
        collaboration_target = 0
        location = self.simulation.get_mobility.get_location(self.simulation.get_clock(), task)

        if self.policy is "asdf":
            collaboration_target = 1

        return collaboration_target