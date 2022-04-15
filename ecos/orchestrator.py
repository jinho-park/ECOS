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
from ecos.event import Event


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
            self.state = np.zeros(5)
            self.action = None
            self.reward = 0
            self.td_error = 0
            self.value = 0
            self.cumulative_reward = 0
            self.epoch = 1
            self.replay = Custom_PER(17, Simulator.get_instance().get_num_of_edge())
            self.id = id
            self.grad = 0

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
                waiting_task_list.append(len(edge.get_waiting_list()))
                available_computing_resource.append(edge.CPU)

            max_waiting_len = max(waiting_task_list)
            waiting_task_list_ = [x/(max_waiting_len+1) for x in waiting_task_list]

            # max_resource = max(available_computing_resource)
            resource_list = []

            for i in range(len(edge_list)):
                exec_list = edge_list[i].get_exec_list()
                require_list = []
                for exe in exec_list:
                    require_list.append(exe.get_input_size()/exe.get_task_deadline())
                resource_list.append(sum(require_list) / available_computing_resource[i])

            state_ = [task.get_remain_size() / 1000] + [task.get_task_deadline() / 1000] + \
                     resource_list + waiting_task_list_ + delay_list
            state = np.array(state_, ndmin=2)

            # edit
            action = ray.get(self.agent.sample_action.remote(state))

            if self.action is not None:
                if isinstance(self.replay, ReplayBuffer):
                    self.replay.store(self.state, self.action, self.reward, state)
                elif isinstance(self.replay, PER):
                    self.replay.store(self.state, self.action, self.reward, state)
                elif isinstance(self.replay, Custom_PER):
                    td_error, value = ray.get(self.agent.sample_value.remote(self.state, self.action, self.reward, state))
                    self.replay.store(self.state, self.action, self.reward, state, td_error.numpy(), value.numpy())

            self.action = np.array(action, ndmin=2)
            self.state = state
            action_sample = np.random.choice(Simulator.get_instance().get_num_of_edge(), p=np.squeeze(action))
            # action_sample = np.argmax(action)
            collaborationTarget = action_sample + 1

            # estimate reward
            # processing time
            processing_time = task.get_input_size() * 3 / available_computing_resource[action_sample]

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

            for i in range(len(waiting_task_list)):
                if i > len(waiting_task_list) - 3:
                    break
                waiting_time += waiting_task_list[i].get_input_size()

            waiting_time /= available_computing_resource[action_sample]

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
            load_balance = (sum(task_list) ** 2) / sum(data) / len(edge_list)

            self.reward = (processing_time + transmission_time + waiting_time) * -1 + \
                          load_balance*0.5
            self.epoch += 1
            task.set_reward(self.reward)

            print("=======================")
            print("state:", state_)
            print("source:", source, " target:", collaborationTarget, "action:", self.action)
            print("reward:", self.reward, "processing:", processing_time,
                  "transmission:", transmission_time, "waiting:", waiting_time, "load_balancing:", load_balance)

            if self.epoch % 10 == 0:
                self.training()

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
                waiting_task_list.append(len(edge.get_waiting_list()))
                available_computing_resource.append(edge.CPU)

            max_waiting_len = max(waiting_task_list)
            waiting_task_list_ = [x / (max_waiting_len + 1) for x in waiting_task_list]

            # max_resource = max(available_computing_resource)
            resource_list = []

            for i in range(len(edge_list)):
                exec_list = edge_list[i].get_exec_list()
                require_list = []
                for exe in exec_list:
                    require_list.append(exe.get_input_size() / exe.get_task_deadline())
                resource_list.append(sum(require_list) / available_computing_resource[i])

            state_ = [task.get_remain_size() / 1000] + [task.get_task_deadline() / 1000] + \
                     resource_list + waiting_task_list_ + delay_list
            state = np.array(state_, ndmin=2)
            # need to add summary

            # edit
            action = ray.get(self.agent.sample_action.remote(state))
            self.action = np.array(action, ndmin=2)
            self.state = state
            # action_sample = np.random.choice(Simulator.get_instance().get_num_of_edge(), p=np.squeeze(action))
            action_sample = np.argmax(action)
            collaborationTarget = action_sample + 1

        return collaborationTarget

    def save_weight(self):
        self.agent.policy.save_weights(self.file_path)

    def training(self):
        if self.training_enable and Simulator.get_instance().get_warmup_time() < Simulator.get_instance().get_clock():
            c_time = time.time()
            # for epc in range(self.epoch):
            if self.replay.get_size() > 0 and self.epoch % 10 == 0:
                print("**************" + str(self.epoch/10) + "***********")
                current_state, actions, rewards, next_state, weight = self.replay.fetch_sample(num_samples=128)

                critic1_loss, critic2_loss, actor_loss, grad_value, alpha_loss = ray.get(self.agent.train.remote(current_state,
                                                                                                     actions,
                                                                                                     rewards,
                                                                                                     next_state,
                                                                                                     weight=weight))

                print("---------------------------")
                print("source:", self.id, "training time:", time.time() - c_time)
                print("actor loss:", actor_loss.numpy(), "critic loss1:", critic1_loss.numpy(),
                      "critic loss2:", critic2_loss.numpy())
                self.loss_file.write("actor_loss: " + str(actor_loss.numpy()) +
                                     " critic_loss1: " + str(critic1_loss.numpy()) +
                                     " critic_loss2: " + str(critic2_loss.numpy()) + "\n")
                self.grad = grad_value

                edge_manager = Simulator.get_instance().get_scenario_factory().get_edge_manager()
                edge_list = edge_manager.get_node_list()
                for edge in edge_list:
                    policy = edge.get_policy()
                    if self.id == policy.get_id():
                        continue

                    grad_ = policy.get_grad()
                    # print("this grad:", self.grad, "target grad:", grad_)

                    if self.grad == 0:
                        percent = 0
                    else:
                        percent = (self.grad - grad_) / self.grad
                    if percent >= 0:
                        percent = percent * -1 + 1
                    else:
                        percent = percent - 1
                    # print("source_grad:", self.grad, "target_grad:", grad_)
                    current_states, actions, rewards, next_state, ranks = self.replay.get_sharing_data(percent + 0.5)

                    if len(current_states) < 1:
                        continue
                    edge_link_list = edge_manager.get_link_list()
                    route_list = edge_manager.get_network().get_path_by_dijkstra(self.id, policy.get_id())
                    set = [self.id, route_list[1]]

                    for link in edge_link_list:
                        link_status = link.get_link()

                        if sorted(set) == sorted(link_status):
                            delay = link.get_delay()

                            msg = {
                                "experience": "transmission",
                                "data": {
                                    "current_state": current_states,
                                    "action": actions,
                                    "reward": rewards,
                                    "next_state": next_state,
                                    "rank": ranks
                                },
                                "route": route_list,
                                "link": link,
                                "delay": delay,
                                "source": policy.get_id()
                            }

                            event = Event(msg, None, delay)
                            Simulator.get_instance().send_event(event)

                            break

                self.agent.update_weights.remote()

    def shutdown(self):
        if self.training_enable:
            ray.shutdown(self.agent)
            self.loss_file.close()

    def get_grad(self):
        return self.grad

    def get_id(self):
        return self.id

    def store_exp(self, list):
        self.replay.replace(list["current_state"], list["action"], list["reward"],
                            list["next_state"], list["rank"], len(list["current_state"]))
