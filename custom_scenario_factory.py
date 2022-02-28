from ecos import Scenario_factory


class Custom_scenario_factory(Scenario_factory):
    def __init__(self, _device_manager,
                 _edge_manager,
                 _cloud_manager):
        self.device_manager = _device_manager
        self.edge_manager = _edge_manager
        self.cloud_manager = _cloud_manager

    def get_device_manager(self):
        super().get_device_manager()
        return self.device_manager

    def get_edge_manager(self):
        super().get_edge_manager()
        return self.edge_manager

    def get_cloud_manager(self):
        super().get_cloud_manager()
        return self.cloud_manager