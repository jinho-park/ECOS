from ecos.simulator import Simulator
from ecos.network_model import Network_model


class CloudManager:
    def __init__(self, cloud_props, network_props):
        self.node_list = list()
        self.cloud_props = cloud_props
        self.cloud_network_props = network_props
        self.cloud_network = None
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1

        #minseon
        self.cloud_id = 0

    #minseon
    def get_cloud_id(self):
        return self.cloud_id

    def get_node_list(self):
        return self.node_list

    def get_state(self):
        return self.state

    def start_entity(self):
        if self.state == 1:
            self.state = 2

        self.create_cloud_server()

        return True

    def shutdown_entity(self):
        if self.state == 2:
            self.state = 1

        return True

    def create_cloud_server(self):
        #
        cloud = Cloud(0, self.cloud_props, Simulator.get_instance().get_clock())
        self.node_list.append(cloud)
        self.cloud_network = Network_model(-1, 0, int(self.cloud_network_props["bandwidth"]),
                                           int(self.cloud_network_props["propagation"]))
        print("Create cloud server")

    def receive_task(self, event):
        cloud = self.node_list[0]

        cloud.task_processing(event.get_task())

    def get_cloud_network(self):
        return self.cloud_network


class Cloud():
    def __init__(self, id, props, time):
        self.CPU = props["mips"]
        self.id = id
        self.exec_list = list()
        self.finish_list = list()
        self.waiting_list = list()
        self.previous_time = time

    def get_cloud_id(self):
        return self.id

    def task_processing(self, task):
        resource_usage = 0

        for task in self.exec_list:
            resource_usage += task.get_allocated_resource()

        if self.CPU - resource_usage > 0:
            self.exec_list.append(task)
        else:
            self.waiting_list.append(task)

    def update_task_state(self, simulationTime):
        timeSpen = simulationTime - self.previous_time

        for task in self.exec_list:
            task.update_finish_time(timeSpen)

        if len(self.exec_list) == 0 and len(self.waiting_list) == 0:
            self.previous_time = simulationTime
