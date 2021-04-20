import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree


def shs_price_for_load(capacity, max_power, shs_characteristics):
    """
    This function returns the price of a Solar Home System of a given an
    average load value as well as a max power based on the price ranges given
    by the price_for_shs DataFrame.

    Parameters
    ----------
    capacity (float):
        Value of the battery capactity required for the shs

    max_power (float):
        Maximum power that shs is supposed to deliver

    shs_characteristics (pandasz.DataFrame):
        Dataframe where each row contains the following inforamtions about the shs:
            'price[$]'
            'capacity[Wh]'
            'max_power[W]'

    Output
    ------
        Price of the cheapest shs fullfiling the capacity and max_power requirement criteria

    """
    for index, row in shs_characteristics.sort_values(by=['capacity[Wh]']).iterrows():
        if row['capacity[Wh]'] >= capacity and row['max_power[W]'] >= max_power:
            return row['price[$]']
    return np.infty


def distance_between_nodes(node1, node2, node_df):
    """
        Returns the distance between two nodes of a node DataFrame.

        Parameters
        ----------
        node1: str
            Label of the first node.
        node2: str
            Label of the second node.

        Returns
        -------
            Distance between the two nodes.
    """
    if not (node1 in node_df.index and node2 in node_df.index):
        raise Warning(f"nodes {node1} and {node2} are not in node_df")
        return np.infty
    return np.sqrt((node_df["x_coordinate"][node1]
                    - (node_df["x_coordinate"][node2])
                    ) ** 2
                   + (node_df["y_coordinate"][node1]
                      - node_df["y_coordinate"][node2]
                      ) ** 2
                   )


def mst_links(nodes_df):
    """
    This function computes the links connecting the set of nodes so that the
    created network forms a minimum spanning tree (MST).

    Parameters
    ----------
    nodes_df (pandas.DataFrame):
        Pandas DataFrame containing the labels and coordinates of the nodes under the form:
                            x_coordinate  y_coordinate
            label                            
            node0           2.0           3.0
            node1           4.0           6.0
            node3           6.0           2.0

    Output
    ------
        Pandas Dataframe containing the (undirected) links composing the MST network.
        Example output:
                            node_a     node_b  distance
            label                                 
            node0, node1    node0  node1    2.2360
            (node1, node2)  node0  node2    2.8284

    """
    X = np.zeros((nodes_df.shape[0], nodes_df.shape[0]))

    for i in range(nodes_df.shape[0]):
        for j in range(nodes_df.shape[0]):
            if i > j:
                index_node_i = nodes_df.index[i]
                index_node_j = nodes_df.index[j]
                X[j][i] = distance_between_nodes(
                    node1=index_node_i,
                    node2=index_node_j,
                    node_df=nodes_df)
    M = csr_matrix(X)

    # run minimum_spanning_tree_function
    Tcsr = minimum_spanning_tree(M)
    A = Tcsr.toarray().astype(float)

    # Create links DataFrame
    links = pd.DataFrame(
        {
            'label': pd.Series([], dtype=str),
            'node_a': pd.Series([], dtype=np.dtype(str)),
            'node_b': pd.Series([], dtype=np.dtype(str)),
            'distance': pd.Series([], dtype=np.dtype(float))
        }
    ).set_index('label')

    for i in range(len(nodes_df.index)):
        for j in range(len(nodes_df.index)):
            if i > j:
                if A[j][i] > 0:
                    links.at[f"({nodes_df.index[i]}, {nodes_df.index[j]})"] = [
                        nodes_df.index[i],
                        nodes_df.index[j],
                        distance_between_nodes(
                            nodes_df.index[i], nodes_df.index[j], nodes_df)
                    ]
    return links


def count_number_of_connections(node_index, links_df):
    """
    This function counts the number of links connected to a node.

    Parameters
    ----------

    node_index (str):
        Index of the node.
    links_df (pandas.DataFrame)
        Pandas DataFrame containing the links connecting the network. In the form
                            node_a     node_b  distance
            label                                 
            node0, node1    node0  node1    2.2360
            (node1, node2)  node0  node2    2.8284

    Output
    ------
        Number of links connecting the node.

    """
    return links_df[
        (links_df['node_a'] == node_index) | (links_df['node_b'] == node_index)
    ].shape[0]


def unitarian_disconnection_price(node_index, nodes_df, shs_characteristics):
    """
    This function returns the price of the shs coresponding to the building
    represented by the node node_index of nodes_df.

    Parameters
    ----------
        node_index (str):
            Index of the node.

        nodes_df (pandas.DataFrame):
            DataFrame containing the nodes of the network in the form
                            x_coordinate  y_coordinate 
                   x_coordinate  y_coordinate    required_capacity  max_power
            label                                                  
            node0  2.0           3.0             90.0               5.0
            node1  4.0           6.0             500.0              20.0
            node2  7.0           10.0            190.0              10.0
            node3  1.0           2.0             1200.0             1000.0

        shs_characteristics (pandas.DataFrame):
            Dataframe where each row contains the following inforamtions about the shs:
                'price[$]'
                'capacity[Wh]'
                'max_power[W]'

    """

    return shs_price_for_load(
        capacity=nodes_df['required_capacity'][node_index],
        max_power=nodes_df['max_power'][node_index],
        shs_characteristics=shs_characteristics
    )


def are_nodes_connected(node_a, node_b, links_df):
    """
    This function returns True is there exists a link in links_df connecting
    node_a and node_b.

    Parameters
    ----------
        node_a (str):
            Index of the first node.

        node_b (str):
            Index of the second node.

        links_df (pandas.DataFrame)
            Pandas DataFrame containing the links connecting the network. In the form
                            node_a   node_b  distance
            label                                 
            node0, node1    node0  node1    2.2360
            (node1, node2)  node0  node2    2.8284
    Output
    ------
        True if there exists a link connecting node_a and node_b in links_df.
    """
    for index_link, row_link in links_df.iterrows():
        if ((row_link['node_a'] == node_a and row_link['node_b'] == node_b)
            or (row_link['node_a'] == node_b and row_link['node_b'] == node_a)
            ):
            return True
    return False


def neighoring_nodes(node_index, links_df):
    """
    This function returns a list of all the nodes that are direct neighbors of the node according to links_df.

    Parameters
    ----------
        node_index (str):
            Label of the node.

        links_df (pandas.DataFrame)
            Pandas DataFrame containing the links connecting the network. In the form
                            node_a     node_b  distance
            label                                 
            node0, node1    node0  node1    2.2360
            (node1, node2)  node0  node2    2.8284
    Output
    ------
        List of the neighboring nodes of node_index.
    """

    neighboring_nodes = []
    for other_node in set(list(links_df['node_a']) + list(links_df['node_b'])):
        if are_nodes_connected(node_index, other_node, links_df):
            neighboring_nodes.append(other_node)
    return neighboring_nodes


def nodes_on_branch(stam_node, branch_first_nodes, links_df, nodes_in_branch):
    """
    This function recursively explores the branch of a tree and returns a list
    of all the nodes on that branch.

    Parameters
    ----------

    stam_node (str):
        Index of the node at the stamm of the branch (the node is
        not considered as part of the branch).
    branch_first_nodes (list):
        List of indices of the next nodes to be explored by the recursive
        function.
    links_df (pandas.DataFrame)
            Pandas DataFrame containing the links connecting the network.
            In the form
                            node_a     node_b  distance
            label                                 
            node0, node1    node0  node1    2.2360
            (node1, node2)  node0  node2    2.8284
    nodes_in_branch (list):
        List of nodes already explored by the recursive function (this list
        contains the nodes identified on the branch and is completed at each
        recursion step).

    Output
    ------
        List of all the nodes on the branches originating at stam_node and
        pointing toward the nodes in branch_first_nodes.
    """
    for branch_node in branch_first_nodes:
        if branch_node not in nodes_in_branch:
            nodes_in_branch.append(branch_node)
    if len(branch_first_nodes) == 0:
        return nodes_in_branch

    for node in branch_first_nodes:
        neighbors = neighoring_nodes(
            node_index=node,
            links_df=links_df)
        downstream_nodes = [node for node in neighbors if (
            node != stam_node and node not in nodes_in_branch)]
        nodes_in_branch += downstream_nodes
        return nodes_on_branch(node, downstream_nodes, links_df, nodes_in_branch)
