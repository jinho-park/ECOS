import json
import os
import tensorflow as tf
import numpy as np

from ecos import Simulator
from ecos import EdgeManager
from ecos import DeviceManager
from ecos import CloudManager
from custom_scenario_factory import Custom_scenario_factory
from ecos import Log


def main():
    configure = "./src/config.json"
    device = "./src/device.json"
    app = "./src/application.json"
    net = "./src/network.json"

    if not os.path.exists('./ecos_result'):
        os.makedirs('./ecos_result')

    result = "./ecos_result/"

    with open(configure, 'r') as f:
        configure_data = json.load(f)

    with open(device, 'r') as f:
        device_data = json.load(f)

    with open(app, 'r') as f:
        app_data = json.load(f)

    with open(net, 'r') as f:
        net_data = json.load(f)

    simul = Simulator.get_instance()

    for episode in range(200):
        for mobile_device in range(int(configure_data["min_num_of_mobile_device"]),
                                   int(configure_data["max_num_of_mobile_device"]),
                                   int(configure_data["mobile_device_counter"])):
            for policy in configure_data["orchestration_policy"]:
                if not simul.initialize(configure_data, net_data, app_data, len(device_data["edge"]), policy):
                    print("Initialization Error")
                    exit(1)

                outputFolderPath = result + "episode" + str(episode) + "_" + policy + "_" + str(mobile_device)+".json"
                folderPath = './results/' + policy + "_" + str(episode)
                simul.set_loss_folder_path(folderPath)
                deviceManager = DeviceManager(device_data["mobile"], mobile_device, device_data["edge"])
                print("Device creating is completed")
                edgeManager = EdgeManager(device_data["edge"], net_data)
                cloudManager = CloudManager(device_data["cloud"], net_data["cloud"])
                scenario_factory = Custom_scenario_factory(deviceManager, edgeManager, cloudManager)
                simul.set_mobile_device(mobile_device)
                simul.set_simulation_factory(scenario_factory)
                print("Start simulator")
                Log.get_instance().sim_start(outputFolderPath, len(device_data["edge"]), simul.get_warmup_time())
                simul.start_simulator()


if __name__ == '__main__':
    main()
    # test()
