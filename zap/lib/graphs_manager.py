import os
import networkx as nx
from zap.settings import *


class GraphManager:

    def __init__(self, username):
        if username:
            self.login = username
            if not os.path.isdir(os.path.join(ROOT_DIR, self.login)):
                os.makedirs(os.path.join(ROOT_DIR, self.login), 0o755)
        self.graph = ''

    @staticmethod
    def show_graph(graph):
        print('Nodes: {}'.format(graph.nodes()))
        print('Edges: {}'.format(graph.edges()))

    def load_graph(self):
        file = os.path.join(os.path.join(ROOT_DIR, self.login), graph_filename)
        if os.path.isfile(file):
            self.graph = nx.read_graphml(file)
            return nx.read_graphml(file)
        else:
            print('ERROR: {} not found.'.format(file))
            return 1

    def save_graph(self):
        file = os.path.join(os.path.join(ROOT_DIR, self.login), graph_filename)
        nx.write_graphml(self.graph, file, encoding='utf-8', prettyprint=True)
        print('SUCCESS: Graph saved.')
        return 0

    def create_root(self, robot_cellnumber):
        self.graph = nx.DiGraph(login=self.login, cellnumber=robot_cellnumber)
        self.graph.add_node(root_node_name)

    def add_node(self, parent, node_name):
        if not parent or not node_name:
            print('ERROR: Parent node or node name not provided.')
            return 1
        dg = nx.DiGraph(self.graph)
        if not dg.has_node(str(parent).lower()):
            print('ERROR: Parent node {} not found in graph'.format(parent).lower())
            return 1
        dg.add_node(str(node_name).lower())
        dg.add_edge(str(parent).lower(), str(node_name).lower())
        print('SUCCESS: {} is now linked to {}.'.format(parent, node_name).lower())
        print('nodes: {}'.format(dg.nodes()))
        print('edges: {}'.format(dg.edges()))
        self.graph = dg
        return 0

    def remove_node(self, node_name):
        if not node_name:
            print('ERROR: Node name not provided.')
            return 1
        dg = nx.DiGraph(self.graph)
        if not dg.has_node(str(node_name).lower()):
            print('ERROR: Node name not found in graph.')
            return 1
        else:
            dg.remove_node(str(node_name).lower())
            print('SUCCESS: Node {} was removed from graph.'.format(node_name).lower())
            return 0

    # def add_alias(self, node_name, alias):
    #     if not node_name or not alias:
    #         print('ERROR: Node name or alias not provided.')
    #         return 1
    #     dg = nx.DiGraph(self.graph)
    #     if not dg.has_node(str(node_name).lower()):
    #         print('ERROR: Node {} found in graph'.format(str(node_name).lower()))
    #         return 1
    #     for i in range(alias_slots):
    #         if i == (alias_slots - 1):
    #             print('ERROR: Limit of aliases slots reached ({}).'.format(alias_slots))
    #             return 1
    #         seq = (str(i), 'alias')
    #         dict_key_alias = '-'.join(seq)
    #         if not dg.node[str(node_name).lower()][str(dict_key_alias).lower()]:
    #             dg.node[str(node_name).lower()][str(dict_key_alias).lower()] = str(alias)
    #             print('SUCCESS: Alias added to node {}.'.format(str(node_name).lower()))

    # def remove_alias(self, node_name, alias):
    #     if not node_name or not alias:
    #         print('ERROR: Node name or alias not provided.')
    #         return 1
    #     dg = nx.DiGraph(self.graph)
    #     if not dg.has_node(str(node_name).lower()):
    #         print('ERROR: Node {} found in graph'.format(str(node_name).lower()))
    #         return 1
    #     for i in range(alias_slots):
    #         seq = (str(i), 'alias')
    #         dict_key_alias = '-'.join(seq)
    #         if dg.node[str(node_name).lower()][str(dict_key_alias).lower()] == str(alias):
    #             del dg.node[str(node_name).lower()][str(dict_key_alias).lower()]
    #             print('SUCCESS: Alias {} was removed from {} node.'.format(str(alias), str(node_name).lower()))

    def get_sucessors(self, node_name):
        dg = nx.DiGraph(self.graph)
        sucessors = dg.successors(node_name)
        return sucessors

    # def search_alias_sucessors(self, position, alias):
    #     dg = nx.DiGraph(self.graph)
    #     for j in self.get_sucessors(position):
    #         node_name = j
    #         for i in range(alias_slots):
    #             seq = (str(i), 'alias')
    #             dict_key_alias = '-'.join(seq)
    #             if dg.node[str(node_name).lower()][str(dict_key_alias).lower()] == str(alias):
    #                 print('SUCCESS: Alias {} was found in node {}.'.format(str(alias), str(node_name).lower()))
    #                 return 0
    #         print('ERROR: Alias {} not found in node {}.'.format(str(alias), str(node_name).lower()))
    #         return 1
