import random
import numpy as np
from ecos.task import Task


# 21.11.17
class Task_generator:
    def __init__(self, _num_of_device, task_prop):
        self.num_of_device = _num_of_device
        self.task_prop = task_prop
        self.taskTypeOfDevice = list()
        self.taskList = list()
        self.taskId = 0

        for i in range(int(self.num_of_device)):
            self.taskTypeOfDevice.append(0)

    def create_task(self, simulationTime):
        self.taskList.clear()

        for i in range(self.num_of_device):
            randomTaskType = -1
            taskTypeSelector = random.randrange(0, 100)
            taskTypePercentage = 0

            for j in self.task_prop["task"]:
                taskTypePercentage += j["percentage"]
                if taskTypeSelector <= taskTypePercentage:
                    randomTaskType = j["type"]
                    break

            if randomTaskType == -1:
                print("task type error")
                exit(1)

            self.taskTypeOfDevice[i] = randomTaskType

            poissonMean = self.task_prop['task'][randomTaskType-1]['generationRate']
            activePeriod = self.task_prop['task'][randomTaskType-1]['activePeriod']
            idlePeriod = self.task_prop['task'][randomTaskType-1]['idlePeriod']
            activePeriodStartTime = random.randrange(10, 10+activePeriod)
            virtualTime = activePeriodStartTime

            while virtualTime < simulationTime:
                interval = np.random.exponential(poissonMean)

                if interval <= 0:
                    print("interval error")
                    continue

                virtualTime += interval

                if virtualTime > activePeriodStartTime + activePeriod:
                    activePeriodStartTime = activePeriodStartTime + activePeriod + idlePeriod
                    virtualTime = round(activePeriodStartTime, 6)
                    continue

                t = Task(self.task_prop["task"][randomTaskType-1], self.taskId)
                t.create_task(round(virtualTime, 6))
                self.taskList.append(t)
                self.taskId += 1

    def get_task_type_of_device(self, deviceId):
        return self.taskTypeOfDevice[deviceId]

    def get_task(self):
        task_list = self.taskList
        return task_list
