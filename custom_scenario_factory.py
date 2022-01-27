from ecos.scenario_factory import Scenario_factory


class Custom_scenario_factory(metaclass=Scenario_factory):
    def __init__(self, _device_manager,
                 _edge_manager,
                 _cloud_manager,
                 _orchestrator):
        self.device_manager = _device_manager
        self.edge_manager = _edge_manager
        self.cloud_manager = _cloud_manager
        self.orchestrator = _orchestrator

    @Scenario_factory
    def get_device_manager(self):
        return self.device_manager

    @Scenario_factory
    def get_edge_manager(self):
        return self.edge_manager

    @Scenario_factory
    def get_cloud_manager(self):
        return self.cloud_manager

    def get_orchestrator(self):
        return self.orchestrator