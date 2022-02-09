import json
from ecos import Simulator
from ecos import Orchestrator
from ecos import EdgeManager
from ecos import DeviceManager
from ecos import CloudManager
from custom_scenario_factory import Custom_scenario_factory

def main():
    configure = "./src/config.json"
    device = "./src/device.json"
    app = "./src/application.json"
    net = "./src/network.json"

    with open(configure, 'r') as f:
        configure_data = json.load(f)

    with open(device, 'r') as f:
        device_data = json.load(f)

    with open(app, 'r') as f:
        app_data = json.load(f)

    with open(net, 'r') as f:
        net_data = json.load(f)

    simul = Simulator.get_instance()
    if not simul.initialize(configure_data, net_data, app_data, len(device_data["edge"])):
        print("Initialization Error")
        exit(1)

    for mobile_device in range(int(configure_data["min_num_of_mobile_device"]),
                               int(configure_data["max_num_of_mobile_device"]),
                               int(configure_data["mobile_device_counter"])):
        for policy in configure_data["orchestration_policy"]:
            deviceManager = DeviceManager(device_data["mobile"], mobile_device, device_data["edge"])
            print("Device creating is completed")
            edgeManager = EdgeManager(device_data["edge"])
            cloudManager = CloudManager(device_data["cloud"], simul.get_clock())
            orchestrator = Orchestrator(policy)
            scenario_factory = Custom_scenario_factory(deviceManager, edgeManager, cloudManager, orchestrator)
            simul.set_mobile_device(mobile_device)
            simul.set_simulation_factory(scenario_factory)
            print("Start simulator")
            simul.start_simulator()

if __name__ == '__main__':
    main()
