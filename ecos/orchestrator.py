import random
import ray
import time
import numpy as np
import os

from ecos.agent import Agent
from ecos.replaybuffer import ReplayBuffer
from ecos.per import PER
from ecos.custom_buffer import Custom_PER
from ecos.simulator import Simulator


class Orchestrator:
    def __init__(self, _policy, id):
        self.policy = _policy

        self.training_enable = False
        # RL training
        if self.policy != "RANDOM":
            self.file_path = './ecos_result/model_' + str(id) + "/"
            folder_path = Simulator.get_instance().get_loss_folder_path()
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
            self.loss_file = open(folder_path + "/loss_log_" + str(id) + ".txt", 'w')
            # create folder
            self.agent = Agent.remote(Simulator.get_instance().get_num_of_edge(), self.file_path)
            self.state = np.zeros(6)
            self.action = None
            self.reward = 0
            self.cumulative_reward = 0
            self.epoch = 1
            self.replay = ReplayBuffer(20, Simulator.get_instance().get_num_of_edge())
            self.id = id

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = Simulator.get_instance()

        if self.policy == "RANDOM":
            num_of_edge = simul.get_num_of_edge()
            selectServer = random.randrange(1, num_of_edge + 1)
            collaborationTarget = selectServer
        elif self.policy == "A2C":
            if not self.training_enable:
                self.training_enable = True

            if Simulator.get_instance().get_clock() < Simulator.get_instance().get_warmup_time():
                num_of_edge = simul.get_num_of_edge()
                selectServer = random.randrange(1, num_of_edge + 1)
                collaborationTarget = selectServer
                return collaborationTarget

            available_computing_resource = []
            waiting_task_list = []
            delay_list = []
            edge_manager = Simulator.get_instance().get_scenario_factory().get_edge_manager()
            edge_list = edge_manager.get_node_list()
            link_list = edge_manager.get_link_list()
            topology = edge_manager.get_network()

            for edge in range(len(edge_list)):
                route = topology.get_path_by_dijkstra(source, edge + 1)
                delay = 0

                for idx in range(len(route)):
                    if idx + 1 >= len(route):
                        break

                    for link in link_list:
                        link_status = link.get_link()
                        set = [route[idx], route[idx + 1]]

                        if sorted(set) == sorted(link_status):
                            delay += link.get_delay()
                            break

                delay_list.append(delay)

            for edge in edge_list:
                waiting_task_list.append(len(edge.get_waiting_list()) / 100)
                available_computing_resource.append(edge.CPU)

            max_resource = max(available_computing_resource)
            resource_list = []

            for i in range(len(edge_list)):
                resource_list.append(available_computing_resource[i] / max_resource)

            state_ = [task.get_remain_size() / 1000] + [task.get_task_deadline() / 1000] + \
                     resource_list + waiting_task_list + delay_list
            state = np.array(state_, ndmin=2)

            if self.action is not None:
                if isinstance(self.replay, ReplayBuffer):
                    self.replay.store(self.state, self.action, self.reward, state)
                elif isinstance(self.replay, PER):
                    self.replay.store(self.state, self.action, self.reward, state)
                elif isinstance(self.replay, Custom_PER):
                    self.replay.store(self.state, self.action, self.reward, state)
                # need to add summary

            # edit
            action = ray.get(self.agent.sample_action.remote(state))
            self.action = np.array(action, ndmin=2)
            self.state = state
            action_sample = np.random.choice(Simulator.get_instance().get_num_of_edge(), p=np.squeeze(action))
            collaborationTarget = action_sample + 1

            # estimate reward
            # processing time
            requirement = task.get_input_size() / task.get_task_deadline()
            processing_time = requirement / available_computing_resource[action_sample]
            processing_time *= min(edge_list[action_sample].get_max_processing(),
                                   len(edge_list[action_sample].get_waiting_list()))
            # transmission time
            network = edge_manager.get_network()
            route = network.get_path_by_dijkstra(source, collaborationTarget)
            transmission_time = 0
            source_ = source

            for dest in route:
                for link in edge_manager.get_link_list():
                    link_status = link.get_link()
                    set = [source_, dest]
                    if sorted(set) == sorted(link_status):
                        delay = link.get_delay()

                        transmission_time += delay
                        break

                source_ = dest

            # buffering time
            waiting_task_list = edge_list[action_sample].get_waiting_list()
            waiting_time = 0

            for task in waiting_task_list:
                waiting_time += task.get_input_size() / task.get_task_deadline()

            waiting_time /= (len(waiting_task_list) * available_computing_resource[action_sample])

            # load_balancing
            task_list = list()

            for edge in edge_list:
                exec_list = edge.get_exec_list()
                wait_list = edge.get_waiting_list()

                num_task = len(exec_list) + len(wait_list)

                if edge_list[action_sample] == edge:
                    num_task += 1
                task_list.append(num_task)

            data = [x ** 2 for x in task_list]
            load_balance = (sum(task_list) ** 2) / sum(data)

            self.reward = (processing_time + transmission_time + waiting_time) * -10 + \
                          load_balance
            self.epoch += 1

            print("=======================")
            print("state:", state_)
            print("source:", source, " target:", collaborationTarget, "action:", self.action)
            print("reward:", self.reward, "processing:", processing_time,
                  "transmission:", transmission_time, "waiting:", waiting_time)

        elif self.policy == "A2C_TEST":
            available_computing_resource = []
            waiting_task_list = []
            delay_list = []
            edge_manager = Simulator.get_instance().get_scenario_factory().get_edge_manager()
            edge_list = edge_manager.get_node_list()
            link_list = edge_manager.get_link_list()
            topology = edge_manager.get_network()

            for edge in range(len(edge_list)):
                route = topology.get_path_by_dijkstra(source, edge + 1)
                delay = 0

                for idx in range(len(route)):
                    if idx + 1 >= len(route):
                        break

                    for link in link_list:
                        link_status = link.get_link()
                        set = [route[idx], route[idx + 1]]

                        if sorted(set) == sorted(link_status):
                            delay += link.get_delay()
                            break

                delay_list.append(delay)

            for edge in edge_list:
                waiting_task_list.append(len(edge.get_waiting_list()) / 100)
                available_computing_resource.append(edge.CPU)

            max_resource = max(available_computing_resource)
            resource_list = []

            for i in range(len(edge_list)):
                resource_list.append(available_computing_resource[i] / max_resource)

            state_ = [task.get_remain_size() / 1000] + [task.get_task_deadline() / 1000] + \
                     resource_list + waiting_task_list + delay_list
            state = np.array(state_, ndmin=2)

            # edit
            action = ray.get(self.agent.sample_action.remote(state))
            self.action = np.array(action, ndmin=2)
            self.state = state
            action_sample = np.random.choice(Simulator.get_instance().get_num_of_edge(), p=np.squeeze(action))
            collaborationTarget = action_sample + 1

        return collaborationTarget

    def save_weight(self):
        self.agent.policy.save_weights(self.file_path)

    def training(self):
        if self.training_enable and Simulator.get_instance().get_warmup_time() < Simulator.get_instance().get_clock():
            print("**************" + str(self.epoch) + "***********")
            c_time = time.time()
            # for epc in range(self.epoch):
            if self.replay.get_size() > 0:
                current_state, actions, rewards, next_state = self.replay.fetch_sample(num_samples=32)

                critic1_loss, critic2_loss, actor_loss, alpha_loss = ray.get(self.agent.train.remote(current_state,
                                                                                                     actions,
                                                                                                     rewards,
                                                                                                     next_state))

                print("---------------------------")
                print("source:", self.id, "training time:", time.time() - c_time)
                print("actor loss:", actor_loss.numpy(), "critic loss1:", critic1_loss.numpy(),
                      "critic loss2:", critic2_loss.numpy())
                self.loss_file.write("actor_loss: " + str(actor_loss.numpy()) +
                                     " critic_loss1: " + str(critic1_loss.numpy()) +
                                     " critic_loss2: " + str(critic2_loss.numpy()) + "\n")
                self.agent.update_weights.remote()

    def shutdown(self):
        if self.training_enable:
            ray.shutdown(self.agent)
            self.loss_file.close()
