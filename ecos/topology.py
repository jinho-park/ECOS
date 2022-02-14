import networkx as nx
import warnings


class Topology:
    def __init__(self):
        self.G = None

    def link_configure(self, config):
        warnings.warn("The configure function will merged with other function",
                      FutureWarning,
                      stacklevel=8)

        self.G = nx.Graph()

        # set bandwidth and propagation delay of link
        for edge in config["topology"]:
            self.G.add_edge(edge["source"], edge["dest"], BW=int(edge["bandwidth"]), PROPA=int(edge["propagation"]))

    def get_path_by_dijkstra(self, src, dst):
        return nx.dijkstra_path(self.G, src, dst, weight="BW")
