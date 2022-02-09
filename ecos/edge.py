from ecos.log import Log
from ecos.simulator import Simulator


class Edge:
    def __init__(self, id, props, policy, time):
        self.CPU = props["CPU"]
        self.id = id
        self.policy = policy
        self.exec_list = list()
        self.finish_list = list()
        self.waiting_list = list()
        self.previous_time = time

    def get_edge_id(self):
        return self.id

    def task_processing(self, task):
        # calculate available resource
        resourceUsage = 0
        print("input task")
        for task in self.exec_list:
            resourceUsage += task.get_allocated_resource()

        if self.CPU - resourceUsage > 0:
            requiredResource = task.get_remain_size() / task.get_task_deadline()
            task.set_allocated_resource(requiredResource)
            self.exec_list.append(task)
        else:
            self.waiting_list.append(task)

    def update_task_state(self, simulationTime):
        timeSpen = simulationTime - self.previous_time

        for task in self.exec_list:
            task.update_remain_size(timeSpen)
            task.set_finish_node()

        if len(self.exec_list) == 0 and len(self.waiting_list) == 0:
            self.previous_time = simulationTime

        for task in self.exec_list:
            if task.get_remain_size() == 0:
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
                task.set_allocated_resource()
                task.set_buffering_time(Simulator.get_instance().get_clock(), 1)
                resourceUsage -= requiredResource
                self.exec_list.append(task)
                self.waiting_list.remove(task)

    def finish_task(self, task):
        task.set_finish_node(1)
        Log.get_instance().record_log(task)
        self.finish_list.remove(task)


