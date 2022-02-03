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
        for task in self.exec_list:
            resourceUsage += task.get_allocated_resource()

        if self.CPU - resourceUsage > 0:
            self.exec_list.append(task)
        else:
            self.waiting_list.append(task)

    def update_task_state(self, simulationTime):
        timeSpen = simulationTime - self.previous_time

        for task in self.exec_list:
            task.update_remain_size(timeSpen)

        if len(self.exec_list) == 0 and len(self.waiting_list) == 0:
            self.previous_time = simulationTime

