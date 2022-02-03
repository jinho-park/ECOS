import sys

from ecos.simulator import Simulator

# 22.01.10
# Time share based algorithm
class Process_schedule:
    def __init__(self, _capacity):
        self.exec_task = list()
        self.wait_task = list()
        self.fini_task = list()
        self.capacity = _capacity
        self.previous_time = 0

    def update_processing(self, current_time):
        time_span = current_time - self.previous_time

        for task in self.exec_task:
            task.update_finish_time()

        if len(self.exec_task) == 0:
            self.previous_time = current_time
            return 0.0

        next_event = sys.maxsize
        for task in self.exec_task:
            if task.task_remain_size == 0:
                self.task_finish()
                self.exec_task.remove(task)

        self.previous_time = current_time

        # estimate finish time
        for task in self.exec_task:
            finish_time = current_time + (task.get_remain_size()
                                          / self.capacity)

            if finish_time - current_time < 0.01:
                finish_time = current_time + 0.01

            if finish_time < next_event:
                next_event = finish_time

        return next_event

    def task_finish(self, task):
        task.finish_task()
        self.fini_task.append(task)
        return

    def task_submit(self, task):
        self.exec_task.append(task)

        return task.get_remain_size() / self.capacity