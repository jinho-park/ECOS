from ecos.edge import Edge
from ecos.event import Event
from ecos.simulator import Simulator
from ecos.orchestrator import Orchestrator


# 22.01.05
class EdgeManager:
    def __init__(self, edge_props):
        self.node_list = list()
        self.edge_props = edge_props
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1
        #minseon
        #self.edge_id = Edge.get_edge_id(self)

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
            edge = Edge(id, self.edge_props[i], Orchestrator(Simulator.get_instance().get_simulation_scenario()), 0)
            id += 1
            self.node_list.append(edge)

    def receive_task_from_edge(self, event):
        # find edge
        msg = event.get_message()

        for node in self.node_list:
            nodeId = node.get_edge_id()

            if nodeId == msg['detail']['dest']:
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
        delay = 0
        msg["detail"]["source"] = source_edge
        msg["detail"]["delay"] = delay
        msg["detail"]["dest"] = dest

        evt = Event(msg, event.get_task(), 0)

        simul.send_event(evt)
