from ecos.sim_setting import Sim_setting

#MM1Queue based network model
class Network_model:
    def __init__(self, id, _net_type):
        self.link_id = id
        # 0: wireless, 1: wire
        self.net_type = _net_type
        self.poissonMean = 0
        self.avgTaskSize = 0
        self.num_send_task = 0

        num_of_task_type = 0

        task_lookup_table = Sim_setting.get_instance().get_task_look_up_table()

        for i in len(task_lookup_table):
            weight = task_lookup_table[i]/100

            if weight != 0:
                self.poissonMean += task_lookup_table[i] * weight
                self.avgTaskSize += task_lookup_table[i] * weight

                num_of_task_type += 1

        self.poissonMean = self.poissonMean/num_of_task_type
        self.avgTaskSize = self.avgTaskSize/num_of_task_type

    def get_link_id(self):
        return self.link_id

    def get_download_delay(self, task):
        self.num_send_task += 1

        sim_setting = Sim_setting.get_instance()

        if self.net_type == 0:
            return self.calculate_MM1(sim_setting.get_wlan_propagation_delay(),
                                      sim_setting.get_wlan_bandwidth())
        else:
            return self.calculate_MM1(sim_setting.get_wlan_propagation_delay(),
                                      sim_setting.get_wlan_bandwidth())

    def calculate_MM1(self, propagation_delay, bandwidth):
        self.avgTaskSize = self.avgTaskSize * 1000 # KB to Byte

        bps = bandwidth * 1000 / 8
        lamda = 1 / self.poissonMean
        mu = bps / self.avgTaskSize

        result = 1 / (mu - lamda * self.num_send_task)

        result += propagation_delay

        if result > 5:
            return -1
        else:
            return result

    def update_send_task(self):
        self.num_send_task -= 1
