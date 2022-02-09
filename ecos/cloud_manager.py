from ecos.event import Event
from ecos.simulator import Simulator


class CloudManager:
    def __init__(self, cloud_props, time):
        self.cloud_props = cloud_props
        self.MIPS = cloud_props["mips"]
        self.processingTaskList = list()
        self.bufferedTaskList = list()
        self.finishTaskList = list()
        self.previousTime = time
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1

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
        print("Create cloud server")

    def receive_task(self, event):
        msg = event.get_message()
        simul = Simulator.get_instance()

        evt = Event(msg, event.get_task())

        simul.send_event(evt)

    def task_processing(self, task):
        resource_usage = 0

        for task in self.processingTaskList:
            resource_usage += task.get_allocated_resource()

        if self.MIPS - resource_usage > 0:
            self.processingTaskList.append(task)
        else:
            self.bufferedTaskList.append(task)

    def update_task_state(self, simulationTime):
        timeSpen = simulationTime - self.previousTime

        for task in self.processingTaskList:
            task.update_finish_time(timeSpen)

        if len(self.processingTaskList) == 0 and len(self.bufferedTaskList) == 0:
            self.previousTime = simulationTime
