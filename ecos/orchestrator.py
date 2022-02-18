import random

from ecos.simulator import Simulator
from ecos.agent import Agent
import numpy as np


class Orchestrator:
    def __init__(self, _policy):
        self.policy = _policy
        self.agent = Agent(Simulator.get_instance().get_num_of_edge())
        self.state = np.zeros(6)
        self.action = None
        self.reward = 0

    def offloading_target(self, task, source):
        collaborationTarget = 0
        simul = Simulator.get_instance()

        if self.policy == "RANDOM":
            num_of_edge = simul.get_num_of_edge()
            selectServer = random.randrange(0, num_of_edge + 1)
            collaborationTarget = selectServer
        elif self.policy == "A2C":
            available_computing_resource = []
            waiting_task_list = []
            link_list = []
            edge_manager = Simulator.get_instance().get_scenario_factory().get_edge_manager()
            edge_list = edge_manager.get_node_list()

            for link in edge_manager.get_link_list():
                link_list.append(link.get_delay())

            for edge in edge_list:
                waiting_task_list.append(len(edge.get_waiting_list()))
                available_computing_resource.append(edge.get_available_resource())

            state = [task.get_remain_size()] + [task.get_task_deadline()] + \
                                       available_computing_resource + waiting_task_list + \
                                       link_list +[source]
            # state = np.array(data_list, ndmin=2)

            # state = ([task.get_remain_size()], [task.get_task_deadline()],
            #                            available_computing_resource, waiting_task_list,
            #                            link_list, [source])
            if self.action is not None:
                self.agent.update_q_network(self.state, self.action, self.reward, state)

            self.action = self.agent.sample_action(state)
            self.state = state
            action_sample = int(self.action.numpy()[0])
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
                    if source_ == link_status[0] and dest == link_status[1]:
                        delay = link.get_delay()

                        transmission_time += delay

                source_ = dest

            # buffering time
            waiting_task_list = edge_list[action_sample].get_waiting_list()
            waiting_time = 0

            for task in waiting_task_list:
                waiting_time = task.get_remain_size() / task.get_task_deadline()

            self.reward = processing_time + transmission_time + waiting_time

        return collaborationTarget
