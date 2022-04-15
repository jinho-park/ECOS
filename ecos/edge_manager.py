from ecos.edge import Edge
from ecos.event import Event
from ecos.simulator import Simulator
from ecos.orchestrator import Orchestrator
from ecos.topology import Topology
from ecos.network_model import Network_model


# 22.01.05
class EdgeManager:
    def __init__(self, edge_props, edge_network_props):
        self.node_list = list()
        self.edge_props = edge_props
        self.edge_network_props = edge_network_props
        self.edge_network = None
        self.edge_link_list = list()
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1
        self.orchestrator = None
        self.waiting_task = list()
        # self.epoch = 1

    #minseon
    def get_node_list(self):
        return self.node_list

    def get_state(self):
        return self.state

    def start_entity(self):
        if self.state == 1:
            self.state = 2

        self.create_edge_server()

        msg = {
            "task": "offloading",
            "detail": {
                "node": "edge"
            }
        }

        event = Event(msg, None, 2)
        Simulator.get_instance().send_event(event)

        return True

    def shutdown_entity(self):
        if self.state == 2:
            self.state = 1

        for edge in self.node_list:
            orche = edge.get_policy()
            orche.shutdown()

        return True

    def create_edge_server(self):
        id = 1
        for i in range(len(self.edge_props)):
            och = Orchestrator(Simulator.get_instance().get_orchestration_policy(), id)
            edge = Edge(id, self.edge_props[i], och, 0, 3)
            id += 1
            self.node_list.append(edge)

        self.edge_network = Topology()
        self.edge_network.link_configure(self.edge_network_props)

        # create link
        for config in self.edge_network_props["topology"]:
            networkModel = Network_model(int(config["source"]), int(config["dest"]),
                                         int(config["bandwidth"]),
                                         int(config["propagation"]))

            self.edge_link_list.append(networkModel)

    def receive_task_from_edge(self, event):
        # find edge
        msg = event.get_message()
        task = event.get_task()

        node = self.node_list[int(msg["detail"]["route"][0]) - 1]
        node.task_processing(task)

    def receive_task_from_device(self, event):
        #
        task = event.get_task()
        self.waiting_task.append(task)

    def offloading(self):
        for task in self.waiting_task:
            source_edge = task.get_source_node()
            node = self.node_list[source_edge - 1]
            dest = node.get_policy().offloading_target(task, source_edge)
            task.set_processing_node(dest)
            task.set_status(1)

            # calculate network delay
            # network module does not complete
            if dest == source_edge:
                msg = {
                    "network" : "transmission",
                    "detail": {
                        "source" : -1,
                        "route" : [source_edge]
                    }
                }

                event = Event(msg, task, 0)
                self.receive_task_from_edge(event)
            elif dest == 0:
                # collaboration target is cloud
                cloudManager = Simulator.get_instance().get_scenario_factory().get_cloud_manager()
                network = cloudManager.get_cloud_network()
                delay = network.get_download_delay(task)

                msg = {
                    "network": "transmission",
                    "detail": {
                        "source": source_edge,
                        "type": 0,
                        "link": network,
                        "delay": delay
                    }
                }

                evt = Event(msg, task, delay)

                Simulator.get_instance().send_event(evt)
            else:
                route_list = self.edge_network.get_path_by_dijkstra(source_edge, dest)
                dest = route_list[1]
                set = [source_edge, dest]
                delay = 0

                # find link
                for link in self.edge_link_list:
                    link_status = link.get_link()

                    if sorted(set) == sorted(link_status):
                        delay = link.get_download_delay(task)

                        msg = {
                            "network": "transmission",
                            "detail": {
                                "source": source_edge,
                                "type": 1,
                                "link": link,
                                "route": route_list,
                                "delay": delay,
                            }
                        }

                        evt = Event(msg, task, delay)

                        Simulator.get_instance().send_event(evt)
                        break

        self.waiting_task = []
        # self.epoch += 1

        # for node in self.node_list:
        #     policy = node.get_policy()
        #     policy.training()

    def get_network(self):
        return self.edge_network

    def get_link_list(self):
        return self.edge_link_list
