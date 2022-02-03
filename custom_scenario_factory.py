from ecos import scenario_factory


class Custom_scenario_factory(scenario_factory.Scenario_factory):
    def __init__(self, _device_manager,
                 _edge_manager,
                 _cloud_manager,
                 _orchestrator):
        self.device_manager = _device_manager
        self.edge_manager = _edge_manager
        self.cloud_manager = _cloud_manager
        self.orchestrator = _orchestrator

    @scenario_factory.Scenario_factory.get_device_manager
    def get_device_manager(self):
        return self.device_manager

    @scenario_factory.Scenario_factory.get_edge_manager
    def get_edge_manager(self):
        return self.edge_manager

    @scenario_factory.Scenario_factory.get_cloud_manager
    def get_cloud_manager(self):
        return self.cloud_manager

    def get_orchestrator(self):
        return self.orchestrator