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

    #minseon
    def get_node_list(self):
        return self.node_list

    def get_state(self):
        return self.state

    def start_entity(self):
        if self.state == 1:
            self.state = 2

        self.create_edge_server()

        return True

    def shutdown_entity(self):
        if self.state == 2:
            self.state = 1

        return True

    def create_edge_server(self):
        id = 1
        for i in range(len(self.edge_props)):
            edge = Edge(id, self.edge_props[i], Orchestrator(Simulator.get_instance().get_orchestration_policy()), 0)
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

        for node in self.node_list:
            nodeId = node.get_edge_id()

            if nodeId == msg['detail']['route'][0]:
                node.task_processing(event.get_task())

    def receive_task_from_device(self, event):
        msg = event.get_message()
        source_edge = int(msg["detail"]["dest"])
        task = event.get_task()
        dest = self.node_list[source_edge - 1].get_policy().offloading_target(task, source_edge)
        simul = Simulator.get_instance()
        msg["detail"]["id"] = 1

        # calculate network delay
        # network module does not complete
        if dest == 0:
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
            delay = 0

            # find link
            for link in self.edge_link_list:
                link_status = link.get_link()

                if source_edge == link_status[0] and dest == link_status[1]:
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

                    evt = Event(msg, event.get_task(), delay)

                    simul.send_event(evt)
                    break

    def get_network(self):
        return self.edge_network

    def get_link_list(self):
        return self.edge_link_list
