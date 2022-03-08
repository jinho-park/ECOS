import random
import ray
import time
import os
import numpy as np

from ecos.agent import Agent
from ecos.replaybuffer import ReplayBuffer
from ecos.per import PER
from ecos.custom_buffer import Custom_PER


@ray.remote
class Orchestrator:
    def __init__(self, _policy, id, simulator):
        self.policy = _policy
        self.Simulator = simulator

        # RL training
        self.agent = Agent(simulator.get_instance().get_num_of_edge())
        self.state = np.zeros(6)
        self.action = None
        self.reward = 0
        self.cumulative_reward = 0
        self.epoch = 1
        self.replay = ReplayBuffer(21, self.Simulator.get_instance().get_num_of_edge())
        self.id = id
        self.file_path = './ecos_result/model_' + str(id) + "/"
        self.training_enable = False

        if len(os.listdir(self.file_path)) > 0:
            self.agent.policy.load_weights(self.file_path)

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = self.Simulator.get_instance()

        if self.policy == "RANDOM":
            num_of_edge = simul.get_num_of_edge()
            selectServer = random.randrange(1, num_of_edge + 1)
            collaborationTarget = selectServer
        elif self.policy == "A2C":
            if not self.training_enable:
                self.training_enable = True

            available_computing_resource = []
            waiting_task_list = []
            delay_list = []
            edge_manager = self.Simulator.get_instance().get_scenario_factory().get_edge_manager()
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
                waiting_task_list.append(len(edge.get_waiting_list()))
                available_computing_resource.append(edge.CPU)

            state_ = [task.get_remain_size()] + [task.get_task_deadline()] + \
                     available_computing_resource + waiting_task_list + \
                     delay_list + [source]
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
            action = self.agent.sample_action(state)
            self.action = np.array(action, ndmin=2)
            self.state = state
            action_sample = np.random.choice(self.Simulator.get_instance().get_num_of_edge(),
                                             p=np.squeeze(action))
            collaborationTarget = action_sample + 1

            # estimate reward
            # processing time
            processing_time = task.get_remain_size() / available_computing_resource[action_sample]
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

                source_ = dest

            # buffering time
            waiting_task_list = edge_list[action_sample].get_waiting_list()
            waiting_time = 0

            for task in waiting_task_list:
                waiting_time = task.get_remain_size() / available_computing_resource[action_sample]

            self.reward = (processing_time + transmission_time + waiting_time) * -1
            self.cumulative_reward += self.reward
            self.epoch += 1

            print("=======================")
            print("source: ", source, " target: ", collaborationTarget)
            print("reward: ", self.reward)
            print("cumulative reward: ", self.cumulative_reward)

        return collaborationTarget

    def save_weight(self):
        self.agent.policy.save_weights(self.file_path)

    def get_parameters(self):
        return self.training_enable, self.replay, self.agent, self.id, self.file_path

    def training(self):
        if self.training_enable:
            c_time = time.time()
            # for epc in range(self.epoch):
            if self.replay.get_size() > 0:
                current_state, actions, rewards, next_state = self.replay.fetch_sample(num_samples=32)

                critic1_loss, critic2_loss, actor_loss, alpha_loss = self.agent.train(current_state, actions,
                                                                                          rewards, next_state)

                print("source:", self.id, "training time:", time.time() - c_time)
                self.agent.update_weights()
                self.agent.policy.save_weights(self.file_path, save_format="tf")
