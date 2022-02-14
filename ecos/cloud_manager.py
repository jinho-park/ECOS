from ecos.simulator import Simulator
from ecos.network_model import Network_model
from ecos.log import Log
from ecos.event import Event
from ecos.orchestrator import Orchestrator
from ecos.topology import Topology


class CloudManager:
    def __init__(self, cloud_props, cloud_network_props):
        self.node_list = list()
        self.cloud_props = cloud_props
        self.cloud_network_props = cloud_network_props
        self.cloud_network = None
        self.cloud_link_list = list()
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1

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
        cloud = Cloud(0, self.cloud_props, Orchestrator(Simulator.get_instance().get_orchestration_policy()), 0)
        self.node_list.append(cloud)
        self.cloud_network = Network_model(-1, 0, int(self.cloud_network_props["bandwidth"]),
                                           int(self.cloud_network_props["propagation"]))
        #self.cloud_network.link_configure(self.cloud_network_props)

        #for config in self.cloud_network_props["topology"]:
        #    networkModel = Network_model(int(config[-1]), int(config[0]),
        #                                 int(config["bandwidth"]),
        #                                 int(config["propagation"]))

        #    self.cloud_link_list.append(networkModel)
        print("Create cloud server")

    def receive_task(self, event):
        msg = event.get_message()
        cloud = self.node_list[0]
        cloud.task_processing(event.get_task())

    def get_cloud_network(self):
        return self.cloud_network

    def get_link_list(self):
        return self.cloud_link_list


class Cloud:
    def __init__(self, id, props, policy, time):
        self.CPU = props["mips"]
        self.id = id
        self.policy = policy
        self.exec_list = list()
        self.finish_list = list()
        self.waiting_list = list()
        self.previous_time = time

    def get_policy(self):
        return self.policy

    def get_cloud_id(self):
        return self.id

    def task_processing(self, task):
        resourceUsage = 0

        for task in self.exec_list:
            resourceUsage += task.get_allocated_resource()

        if self.CPU - resourceUsage > 0:
            requiredResource =  task.get_remain_size() / task.get_task_deadline()
            task.set_allocated_resource(requiredResource)
            self.exec_list.append(task)
            msg = {
                "task": "check",
                "detail": {
                    "node": "cloud",
                    "id": self.id
                }
            }
            event = Event(msg, None, task.get_task_deadline())
            Simulator.get_instance().send_event(event)
        else:
            self.waiting_list.append(task)

    def update_task_state(self, simulationTime):
        timeSpen = simulationTime - self.previous_time

        for task in self.exec_list:
            allocatedResource = task.get_allocated_resource()
            remainSize = task.get_remain_size() - (allocatedResource * timeSpen)
            task.set_remain_size(remainSize)
            task.set_finish_node(1)

        if len(self.exec_list) == 0 and len(self.waiting_list) == 0:
            self.previous_time = simulationTime

        for task in self.exec_list:
            if task.get_remain_size() <= 0:
                self.exec_list.remove(task)
                self.finish_list.append(task)
                self.finish_task(task)

        if len(self.waiting_list) > 0:
            resourceUsage = 0

            for task in self.exec_list:
                resourceUsage += task.get_allocated_resource()

            for task in self.waiting_list:
                if resourceUsage <= 0:
                    break

                requiredResource = task.get_remain_size() / task.get_task_deadline()

                if requiredResource > resourceUsage:
                    break

                task.set_allocated_resource(requiredResource)
                task.set_buffering_time(Simulator.get_instance().get_clock(), 1)
                resourceUsage -= requiredResource
                self.exec_list.append(task)
                self.waiting_list.remove(task)

            # add event
            nextEvent = 99999999999999
            for task in self.exec_list:
                remainingLength = task.get_remain_size()
                estimatedFinishTime = (remainingLength / task.get_allocated_resource())

                if estimatedFinishTime < 1:
                    estimatedFinishTime = 1

                if estimatedFinishTime < nextEvent:
                    nextEvent = estimatedFinishTime

            msg = {
                "task": "check",
                "detail": {
                    "node": "cloud",
                    "id": self.id
                }
            }
            event = Event(msg, None, nextEvent)
            Simulator.get_instance().send_event(event)

    def finish_task(self, task):
        # 1 means edge node
        task.set_finish_node(2)
        task.set_processing_time(Simulator.get_instance().get_clock(), 1)
        task.set_end_time(Simulator.get_instance().get_clock())
        Log.get_instance().record_log(task)
        self.finish_list.remove(task)