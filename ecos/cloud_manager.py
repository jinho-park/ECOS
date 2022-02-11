from ecos.event import Event
from ecos.simulator import Simulator
from ecos.orchestrator import Orchestrator
from ecos.log import Log

class CloudManager:
    def __init__(self, cloud_props, time):
        self.node_list = list()
        self.cloud_props = cloud_props
        self.previousTime = time
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1

        #minseon
        #self.cloud_id = 0

    #minseon
    #def get_cloud_id(self):
    #    return self.cloud_id

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
        #cloud = Cloud(0, self.cloud_props, Simulator.get_instance().get_clock())
        cloud = Cloud(0, self.cloud_props, Orchestrator(Simulator.get_instance().get_simulation_scenario()), 0)
        self.node_list.append(cloud)
        print("Create cloud server")


    #수정필요
    def receive_task(self, event):
        msg = event.get_message()

        simul = Simulator.get_instance()

        evt = Event(msg, event.get_task())

        simul.send_event(evt)


class Cloud():
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
        resource_usage = 0

        for task in self.exec_list:
            resource_usage += task.get_allocated_resource()

        if self.CPU - resource_usage > 0:
            requiredResource = task.get_remain_size()/task.get_task_deadline()
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

    #def update_task_state(self, simulationTime):
    #    timeSpen = simulationTime - self.previous_time

    #    for task in self.exec_list:
    #        task.update_finish_time(timeSpen)

    #    if len(self.exec_list) == 0 and len(self.waiting_list) == 0:
    #        self.previous_time = simulationTime

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
                task.set_buffering_time(
                    Simulator.get_instance().get_clock() - task.get_birth_time() - task.get_network_delay())
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
        task.set_finish_node(1)
        task.set_processing_time(Simulator.get_instance().get_clock() - task.get_birth_time() - task.get_buffering_time() - task.get_network_delay())
        task.set_end_time(Simulator.get_instance().get_clock())
        Log.get_instance().record_log(task)
        self.finish_list.remove(task)