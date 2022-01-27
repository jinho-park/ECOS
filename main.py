import json
from ecos.simulator import Simulator
from ecos.orchestrator import Orchestrator
from ecos.edge_manager import EdgeManager
from ecos.device_manager import DeviceManager
from custom_scenario_factory import Custom_scenario_factory

def main():
    configure = "/src/config.json"
    device = "/src/device.json"
    app = "/src/device.json"

    with open(configure, 'r') as f:
        configure_data = json.load(f)

    with open(device, 'r') as f:
        device_data = json.load(f)

    with open(app, 'r') as f:
        app_data = json.load(f)

    simul = Simulator.get_instance()
    simul.initialize(configure_data['simulation_time'], configure_data['simul_scenario'])

    for mobile_device in range(int(configure_data["min_num_of_mobile_device"]),
                               int(configure_data["max_num_of_mobile_device"]),
                               int(configure_data["mobile_device_counter"])):
        for policy in range(configure_data["orchestration_policy"]):
            deviceManager = DeviceManager(device_data["mobile"])
            edgeManager = EdgeManager(device_data["edge"])
            cloudManager =
            orchestrator = Orchestrator(policy)
            scenario_factory = Custom_scenario_factory(deviceManager,
                                                       edgeManager,
                                                       cloudManager,
                                                       orchestrator)
            simul.set_mobile_device(mobile_device)
            simul.set_simulation_factory(scenario_factory)
            simul.start_simulator()

    if simul.initialize() is False:
        print("Simulator initialization error!")
        exit(1)

if __name__ == '__main__':
    main()
