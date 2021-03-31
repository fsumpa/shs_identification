import pandas as pd
import numpy as np





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

    shs_characteristics (pd.DataFrame):
        Dataframe where each row contains the following inforamtions about the shs:
            'price[$]'
            'capacity[Wh]'
            'max_power[W]'
    
    Output
    ------
        Price of the cheapest shs fullfiling the capacity and max_power requirement criteria

    """
    shs_sorted_by_capacity = list(shs_characteristics.sort_values(by=['capacity[Wh]']).index)
    for index, row in shs_characteristics.sort_values(by=['capacity[Wh]']).iterrows():
        if row['capacity[Wh]'] >= capacity and row['max_power[W]'] >= max_power:
            return row['price[$]']
    return np.infty


def mst_links(nodes):
    """
    This function computes the links connecting the set of nodes so that the
    created network forms a minimum spanning tree (MST).

    Parameters
    ----------
    nodes (pd.DataFrame):
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
                            from     to  distance
            label                                 
            node0, node1    node0  node1    2.2360
            (node1, node2)  node0  node2    2.8284

    """
    X = np.zeros((nodes.shape[0], nodes.shape[0]))
        
    for i in range(nodes.shape[0]):
        for j in range(nodes.shape[0]):
            if i > j:
                index_node_i = nodes.index[i]
                index_node_j = nodes.index[j]
                X[j][i] = grid.distance_between_nodes(index_node_i,
                                                              index_node_j)

