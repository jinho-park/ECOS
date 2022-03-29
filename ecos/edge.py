from ecos.log import Log
from ecos.simulator import Simulator
from ecos.event import Event


class Edge:
    def __init__(self, id, props, policy, time, proc_num):
        self.CPU = props["mips"]
        self.id = id
        self.policy = policy
        self.num_of_max_processing = proc_num
        self.exec_list = list()
        self.finish_list = list()
        self.waiting_list = list()
        self.previous_time = time

    def get_policy(self):
        return self.policy

    def get_edge_id(self):
        return self.id

    def task_processing(self, task):
        # calculate available resource

        task.set_status(2)

        if len(self.exec_list) < 3 and len(self.waiting_list) < 1:
            self.exec_list.append(task)
            require_list = [x.get_input_size()/x.get_task_deadline() for x in self.exec_list]
            ratio = (task.get_input_size()/task.get_task_deadline())/sum(require_list)
            task.set_allocated_resource(self.CPU * ratio)
            expected_finish_time = task.get_remain_size() / (self.CPU * ratio)
            msg = {
                "task": "check",
                "detail": {
                    "node": "edge",
                    "id": self.id
                }
            }
            event = Event(msg, None, round(expected_finish_time, 3))
            self.previous_time = Simulator.get_instance().get_clock()
            Simulator.get_instance().send_event(event)
            if expected_finish_time > 10:
                print("error finish time")
        else:
            self.waiting_list.append(task)

    def update_task_state(self, simulationTime):
        timeSpen = round(simulationTime - self.previous_time, 6)

        for task in self.exec_list:
            allocatedResource = task.get_allocated_resource()
            remainSize = round(task.get_remain_size() - (allocatedResource * timeSpen), 0)
            task.set_remain_size(remainSize)

        if len(self.exec_list) == 0 and len(self.waiting_list) == 0:
            self.previous_time = simulationTime
            return

        for task in self.exec_list:
            if task.get_remain_size() <= 0:
                self.exec_list.remove(task)
                self.finish_list.append(task)
                self.finish_task(task)

        if len(self.waiting_list) > 0:
            for task in self.waiting_list:
                if len(self.exec_list) >= 3:
                    break

                task.set_buffering_time(Simulator.get_instance().get_clock(), 1)
                self.exec_list.append(task)
                self.waiting_list.remove(task)

        # allocate computing resource according to task requirement
        requirement_list = [x.get_input_size()/x.get_task_deadline() for x in self.exec_list]
        for task in self.exec_list:
            requirement = task.get_input_size()/task.get_task_deadline()
            task.set_allocated_resource((requirement / sum(requirement_list)) * self.CPU)

        if len(self.exec_list) > 0:
            # add event
            nextEvent = 99999999999999
            for task in self.exec_list:
                remainingLength = task.get_remain_size()
                estimatedFinishTime = (remainingLength / task.get_allocated_resource())

                if estimatedFinishTime < 0.001:
                    estimatedFinishTime = 0.001

                if estimatedFinishTime < nextEvent:
                    nextEvent = estimatedFinishTime

            msg = {
                "task": "check",
                "detail": {
                    "node": "edge",
                    "id": self.id
                }
            }
            event = Event(msg, None, nextEvent)
            Simulator.get_instance().send_event(event)

        self.previous_time = simulationTime

    def finish_task(self, task):
        # 1 means edge node
        task.set_finish_node(1)
        task.set_processing_time(self.previous_time, 1)
        task.set_end_time(self.previous_time)
        Log.get_instance().record_log(task)
        self.finish_list.remove(task)

    def get_exec_list(self):
        return self.exec_list

    def get_waiting_list(self):
        return self.waiting_list

    def get_available_resource(self):
        resourceUsage = 0

        for task in self.exec_list:
            resourceUsage += task.get_allocated_resource()

        return self.CPU - resourceUsage

    def get_max_processing(self):
        return self.num_of_max_processing
