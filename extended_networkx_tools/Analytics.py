import copy
import queue
from typing import List, Dict, Tuple
import warnings

import networkx as nx
import numpy as np
from numpy import linalg

try:
    from Solver import Solver
except ImportError:
    from .Solver import Solver


class Analytics:

    @staticmethod
    def get_neighbour_matrix(nxg: nx.Graph):
        warnings.warn("Function depreciated, please use get_adjacency_matrix(nxg, True) instead",
                      DeprecationWarning)
        return Analytics.get_adjacency_matrix(nxg, True)

    @staticmethod
    def get_adjacency_matrix(nxg: nx.Graph, self_assignment=False) -> List[List[int]]:
        """
        Creates a neighbour matrix for a specified graph: g, each row represents a node in the graph
        where the values in each column represents if there is an edge or not between those nodes.

        :param nxg: networkx bi-directional graph object.
        :type nxg: nx.Graph
        :param self_assignment: Whether or not to use self assignment in the graph. Used for convergence rate.
        :type nxg: bool
        :return A: List of rows, representing the adjacency matrix.
        :rtype: List[List[float]]
        """
        # Sort the nodes in the graph
        s_nodes = list(nxg.nodes())
        s_nodes.sort()
        # Get the dimension of each row
        dim = len(s_nodes)

        mx = []
        for node in nxg.nodes():
            row = [0] * dim
            # Get the index of the current node
            node_index = s_nodes.index(node)
            if self_assignment:
                row[node_index] = 1
            for neighbour in nxg.neighbors(node):
                node_index = s_nodes.index(neighbour)
                row[node_index] = 1
            mx.append(row)
        return mx

    @staticmethod
    def get_stochastic_neighbour_matrix(nxg: nx.Graph = None, adjacency_matrix: List[List[int]] = None) -> List[List[float]]:
        """
        Creates a stochastic adjacency matrix for a specified graph: g, each row represents a node in the graph
        where the values in each column represents if there is an edge or not between those nodes.
        The values for each neighbour is represented by 1/(number of neighbours), if no edge exists this value is 0.

        :param nxg: Networkx bi-directional graph object.
        :type nxg: nx.Graph
        :param adjacency_matrix: Self assigned adjacency matrix.
        :type adjacency_matrix: List[List[int]]
        :return A: List of rows, representing the adjacency matrix.
        :rtype: List[List[float]]
        """
        if nxg is None and adjacency_matrix is None:
            raise ValueError('At least one parameter of nxg or adjacency_matrix needs to be provided')

        # If we wasn't provided with the adjacency matrix, get it.
        if adjacency_matrix is None:
            # Get the adjacency matrix
            mx = Analytics.get_adjacency_matrix(nxg, True)
        else:
            mx = adjacency_matrix

        # Iterate over each row
        for row_id, _ in enumerate(mx):
            # Calculate the sum for each row
            row_sum = sum(mx[row_id])
            # Divide each node in the row with the sum of the row
            mx[row_id] = list(map(lambda x: (x / row_sum), mx[row_id]))

        # Working solution that might however be worse than the previous solution.
        # mx = list(map(lambda row: list(map(lambda cell: cell / sum(row), row)), mx))

        return mx

    @staticmethod
    def get_eigenvalues(mx: List[List[float]]) -> np.ndarray:
        """
        Simple function to retrieve the eigenvalues of a matrix.

        :param mx: A matrix made up of nested lists.
        :return: List of eigenvalues of the provided matrix.
        :rtype: List[float]
        """
        return linalg.eigvalsh(mx)

    @staticmethod
    def second_largest(numbers: List[float], sorted_list: bool = False) -> float:
        """
        Simple function to return the 2nd largest number in a list of numbers.

        :param numbers: A list of numbers
        :param sorted_list: If the list is sorted or not
        :return: The 2nd largest number in the list numbers
        :rtype: float

        """
        if sorted_list:
            return numbers[len(numbers)-2]

        count = 0
        m1 = m2 = float('-inf')
        for x in numbers:
            count += 1
            if x > m2:
                if x >= m1:
                    m1, m2 = x, m1
                else:
                    m2 = x
        return m2 if count >= 2 else None

    @staticmethod
    def second_smallest(numbers: List[float], sorted_list: bool = False) -> float:
        """
        Simple function to return the 2nd smallest number in a list of numbers.

        :param numbers: A list of numbers
        :param sorted_list: If the list is sorted or not
        :return: The 2nd smallest number in the list numbers
        :rtype: float
        """
        if sorted_list:
            return numbers[1]

        count = 0
        m1 = m2 = float('inf')
        for x in numbers:
            count += 1
            if x < m2:
                if x <= m1:
                    m1, m2 = x, m1
                else:
                    m2 = x
        return m2 if count >= 2 else None

    @staticmethod
    def convergence_rate(nxg: nx.Graph = None, stochastic_neighbour_matrix: List[List[float]] = None) -> float:
        """
        Function to retrieve the 2nd largest eigenvalue in the adjacency matrix of a graph

        :param nxg: networkx bi-directional graph object
        :type nxg: nx.Graph
        :param stochastic_neighbour_matrix: The stochastic neighbour matrix of the given graph.
        :type stochastic_neighbour_matrix: List[List[float]]
        :return: The 2nd largest eigenvalue of the adjacency matrix
        :rtype: float
        """
        if nxg is None and stochastic_neighbour_matrix is None:
            raise ValueError('At least one parameter of nxg or stochastic_neighbour_matrix needs to be provided')

        # If we wasn't provided with the adjacency matrix, get it.
        if stochastic_neighbour_matrix is None:
            # Get the adjacency matrix
            A = Analytics.get_stochastic_neighbour_matrix(nxg)
        else:
            A = stochastic_neighbour_matrix

        ev = Analytics.get_eigenvalues(A)
        return Analytics.second_largest(ev, True).real

    @staticmethod
    def convergence_rate2(nxg: nx.Graph) -> float:
        """
        Function to retrieve convergence rate based on an alternate approach.

        :param nxg: networkx bi-directional graph object
        :type nxg: nx.Graph
        :return: Alternate convergence rage
        :rtype: float
        """
        A = Analytics.get_stochastic_neighbour_matrix(nxg)
        ev = Analytics.get_eigenvalues(A)
        largest = ev[len(ev)-1].real
        smallest = ev[0].real
        second_largest = Analytics.second_largest(ev, True).real
        return max(
            largest - abs(second_largest),
            largest - abs(smallest)
        )

    @staticmethod
    def total_edge_cost(nxg: nx.Graph) -> int:
        """
        Calculates the total cost of all edges in the given graph

        :param nxg: A networkx object with nodes and edges.
        :type nxg: nx.Graph
        :return: The total cost of all edges in the graph.
        :rtype: float
        """
        total = 0
        edges = nxg.edges(data=True)

        for edge in edges:
            if 'weight' in edge[2]:
                total += edge[2]['weight']
            
        return total

    @staticmethod
    def hypothetical_max_edge_cost(nxg: nx.Graph) -> float:
        """
        Calculates the hypothetical total edge cost if the graph were to be complete.

        :rtype: float
        :param nxg: The graph to calculate the hypothetical edge cost of.
        :return: The total edge cost if the graph were complete.
        """
        complete_graph = copy.deepcopy(nxg)
        complete_graph = Solver.complete(complete_graph)
        total_edge_cost = Analytics.total_edge_cost(complete_graph)
        del complete_graph
        return total_edge_cost

    @staticmethod
    def get_distance_distribution(nxg: nx.Graph) -> Dict[int, int]:
        """
        Makes a list representing the distribution of longest shortest paths between every node
        in the graph.

        :rtype: Dict[int, int]
        :param nxg: A given graph with edges.
        :return: A dict with a distribution of the longest shortest paths between nodes.
        """
        warnings.warn("Function depreciated, please use get_eccentricity_distribution(nxg) instead",
                      DeprecationWarning)

        # Get a list of all paths
        paths = list(nx.networkx.all_pairs_shortest_path_length(nxg))
        # Create an empty dict of distance distributions
        distributions = {}
        # Iterate over each path
        for origin, path in paths:
            # Make sure we don't check the same path twice
            max_node_distance = -1
            for dest in range(0, len(path)):
                # Get the actual shortest distance between 2 nodes
                max_node_distance = max(max_node_distance, path.get(dest))
                # Make sure we create the distance first, then add one to it
            if max_node_distance is not -1:
                if max_node_distance not in distributions:
                    distributions[max_node_distance] = 1
                else:
                    distributions[max_node_distance] += 1

        return distributions

    @staticmethod
    def get_eccentricity_distribution(nxg: nx.Graph) -> Dict[int, int]:
        """
        Makes a list representing the distribution of longest shortest paths between every node
        in the graph.

        :rtype: Dict[int, int]
        :param nxg: A given graph with edges.
        :return: A dict with a distribution of the longest shortest paths between nodes.
        """
        # Get the eccentricity of the graph
        eccentricities = nx.eccentricity(nxg)
        # Create a distribution dictionary
        distributions = {}

        # Iterate over the eccentricities
        for nid, eccentricity in eccentricities.items():
            # Make sure an occurrence if the eccentricity exists in the distribution dict
            if eccentricity not in distributions:
                distributions[eccentricity] = 0

            # Add one to the eccentricity distribution
            distributions[eccentricity] += 1

        return distributions

    @staticmethod
    def is_nodes_connected(nxg: nx.Graph, origin: int, destination: int) -> bool:
        """
        Checks if two nodes are connected with each other using a BFS approach.

        :param nxg: The grapg that contains the two nodes.
        :param origin: The origin node id to check from.
        :param destination: The destination node to check the connectivity to.
        :return: True if there's a connection between the nodes, otherwise False.
        """
        # Create a set of seen nodes
        seen = set()
        # Create a queue
        q = queue.Queue()

        # Add the start node
        q.put(origin)

        # Iterate while the queue is not empty
        while not q.empty():
            # Get the first element of the queue
            node_id = q.get()
            # If we're at the destination, return True
            if node_id == destination:
                return True

            # Otherwise, add the node to seen
            seen.add(node_id)
            # Iterate over the neighbours, but discard the first element
            # since it should be the origin
            for _, neighbour in nxg.edges(node_id):
                # If we haven't seen it, add it to the queue
                if neighbour not in seen:
                    q.put(neighbour)

        # If we've reached here we haven't found the other node. If so, return False
        return False

    @staticmethod
    def get_node_dict(nxg: nx.Graph) -> Dict[int, Tuple[int, int]]:
        """
        Converts a networkx object to a dict with nodes and their positions.
        Can be used to recreate a new graph with Creator.from_dict().

        :rtype: Dict[int, Tuple[int, int]]
        :param nxg: The graph to get the nodes from.
        :return: A dict of nodes with their corresponding positions.
        """
        nodes = {}
        for node in nxg.nodes(data=True):
            nodes[node[0]] = (node[1]['x'], node[1]['y'])
        return nodes

    @staticmethod
    def get_edge_dict(nxg: nx.Graph) -> Dict[int, List[int]]:
        """
        Converts a networkx object to a dict with edges and their neighbours.
        Can be used to recreate a new graph with Creator.from_dict().

        :rtype: Dict[int, List[int]]
        :param nxg: The graph to get the edges from.
        :return: A neighbour list for all nodes.
        """
        edges = {}
        for origin, dest in nxg.edges():
            if origin not in edges:
                edges[origin] = []
            edges[origin].append(dest)
        return edges

    @staticmethod
    def get_average_eccentricity(nxg: nx.Graph) -> float:
        """
        Calculates the average eccentricity from the given graph.

        :rtype: float
        :param nxg: The graph to get the average eccentricity from.
        :return: The average eccentricty from the graph.
        """
        distribution = Analytics.get_eccentricity_distribution(nxg)
        occurrence = 0
        count = 0
        for d, c in distribution.items():
            occurrence += d*c
            count += c
        return occurrence/count

    @staticmethod
    def get_degree_matrix(nxg: nx.Graph) -> List[List[int]]:
        # Sort the nodes in the graph
        s_nodes = list(nxg.nodes())
        s_nodes.sort()
        # Get the dimension of each row
        dim = len(s_nodes)

        mx = []
        for node in nxg.nodes():
            row = [0] * dim
            # Get the index of the current node
            node_index = s_nodes.index(node)
            row[node_index] = nx.degree(nxg, node_index)
            mx.append(row)
        return mx

    @staticmethod
    def get_laplacian_matrix(nxg: nx.Graph) -> List[List[int]]:
        """
        Calculates the laplacian matrix based on a given graph.

        :param nxg: The graph to get the laplacian matrix from.
        :return: The laplacian matrix, such as L = D - A where
                    D = Degree matrix and
                    A = Adjacency matrix
        """
        laplacian_matrix = []
        degree_matrix = Analytics.get_degree_matrix(nxg)
        adjacency_matrix = Analytics.get_adjacency_matrix(nxg)

        dimension = len(adjacency_matrix)

        for r in range(0, dimension):
            row = [0] * dimension
            for c in range(0, dimension):
                row[c] = degree_matrix[r][c] - adjacency_matrix[r][c]
            laplacian_matrix.append(row)

        return laplacian_matrix

    @staticmethod
    def is_graph_connected(laplacian_matrix: List[List[int]]):
        """
        Checks whether a given graph is connected based on its laplacian matrix.

        :param laplacian_matrix: The laplacian matrix, representing the graph.
        :return: Whether it's connected or not.
        """
        ev = Analytics.get_eigenvalues(laplacian_matrix)
        second_smallest = Analytics.second_smallest(ev, True).real

        # Check if it's above a certain threshold due to floating point errors
        return second_smallest > 1e-8
