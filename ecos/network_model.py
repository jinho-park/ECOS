from ecos.simulator import Simulator


# MM1Queue based network model
class Network_model:
    def __init__(self, source, dest, _bandwidth, _propagation):
        self.link = [source, dest]
        self.poissonMean = 1
        self.bandwidth = _bandwidth
        self.propagation = _propagation
        self.sumTaskSize = 100
        self.send_task_list = list()
        self.send_task_type = list()

        task_props = Simulator.get_instance().get_task_look_up_table()

        for i in range(len(task_props["task"])):
            self.send_task_type.append(0)

    def get_link(self):
        return self.link

    def get_download_delay(self, task):
        self.send_task_list.append(task)
        self.send_task_type[task.get_task_type() - 1] += 1

        self.update_MM1_parameter()

        return self.calculate_MM1(self.propagation, self.bandwidth)

    def update_MM1_parameter(self):
        size_sum = 0
        poisson = 0

        task_props = Simulator.get_instance().get_task_look_up_table()

        for task in self.send_task_list:
            taskSize = task.get_input_size()
            size_sum += taskSize

        index = 0
        for num in self.send_task_type:
            weight = num / sum(self.send_task_type)

            if weight != 0:
                poisson += (int(task_props["task"][index]["generationRate"]) * weight)

            index += 1

        self.poissonMean = poisson / len(self.send_task_list)
        self.sumTaskSize = size_sum

    def calculate_MM1(self, propagation_delay, bandwidth):
        taskSize = self.sumTaskSize * 1000 # KB to Byte
        propagation_delay_ = propagation_delay / 1000

        bps = bandwidth * 1000000 / 8
        lamda = 1 / self.poissonMean
        mu = bps / taskSize

        result = 1 / (mu - lamda * (len(self.send_task_list)))

        if result < 0:
            result = 0

        result += propagation_delay_

        return round(result, 6)

    def update_send_task(self, task):
        self.send_task_list.remove(task)
        self.send_task_type[task.get_task_type() - 1] -= 1

    def get_delay(self):
        return self.calculate_MM1(self.propagation, self.bandwidth)
