from ecos.task import Task
from ecos.sim_setting import Sim_setting
from ecos.edge import Edge
from ecos.event import Event
from ecos.simulator import Simulator


# 22.01.05
class EdgeManager:
    def __init__(self, edge_props, orchestrate=None):
        self.edge_id = 0
        self.edge_list = list()
        self.edge_props = edge_props
        self.orchestrate_policy = orchestrate
        self.simSetting = Sim_setting()
        # 1 : FINISHED, 2 : RUNNABLE
        self.state = 1

    def get_state(self):
        return self.state

    def run(self):
        if self.state == 1:
            self.state = 2

        return True

    def shutdown_entity(self):
        if self.state == 2:
            self.state = 1

        return True

    def create_edge_server(self):
        for i in self.edge_props.length:
            edge = Edge(self.edge_id, self.edge_props[i], self.orchestrate_policy)
            self.edge_id += 1
            self.edge_list.append(edge)

    def receive_task_from_edge(self, event):
        # find edge
        msg = event.get_message()

        for node in self.edge_list:
            nodeId = node.get_edge.id()

            if nodeId == msg['detail']['dest']:
                node.task_processing(event.get_task())

    def receive_task_from_device(self, event):
        msg = event.get_message()
        dest = self.orchestrate_policy.get_target(event.get_task())
        simul = Simulator.get_instance()
        msg["detail"]["dest"]["id"] = 1

        # calculate network delay
        # network module does not complete
        delay = 0
        msg["detail"]["delay"] = delay
        msg["detail"]["dest"] = dest

        evt = Event(msg, event.get_task())

        simul.send_event(evt)