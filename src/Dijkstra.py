import osmnx as ox
import networkx as nx
from ipyleaflet import Map
import numpy as np
from math import *
import math
import matplotlib.pyplot as plt
import json
import requests
import pandas as pd
from pandas import json_normalize
import folium
import timeit
from time import time
import sqlite3

start = timeit.default_timer()

place = 'Iloilo City, Philippines'
G = ox.graph_from_place(place, clean_periphery=True, simplify=True, network_type= 'drive')

input_origin = input('Origin: ')
input_destination = input('Destination: ')

class Get_Origin:
    
    global result
    
    data1 = sqlite3.connect(database = "test2.db")
    cursor1 = data1.cursor()
    orig = ("SELECT * from Data_Loc WHERE loc = '%s'" %(input_origin))
    cursor1.execute(orig)
    result = cursor1.fetchall()
    for x in result:
        origin = (x[3])
        
    
class Get_Destination:
    global result
    
    data2 = sqlite3.connect(database = "test2.db")
    cursor2 = data2.cursor()
    dest = ("SELECT * from Data_Loc WHERE loc = '%s'" %(input_destination))
    cursor2.execute(dest)
    result = cursor2.fetchall()
    for y in result:
        destination = (y[3])
        
    
class Get_LatLong:
    global result
    
    data = sqlite3.connect(database = "test2.db")
    cursor = data.cursor()
    lat = ("SELECT * from Data_Loc WHERE loc = '%s'" %(input_origin))
    cursor.execute(lat)
    result = cursor.fetchall()
    for y in result:
        latitude = (y[1])
        longitude = (y[2])
    
lat = Get_LatLong.latitude
long = Get_LatLong.longitude

orig_point = Get_Origin.origin

dest_point = Get_Destination.destination

highlighted = [orig_point, dest_point]

nc = ['r' if node in highlighted else '#336699' for node in G.nodes()]
ns = [50 if node in highlighted else 8 for node in G.nodes()]

ox.speed.add_edge_speeds(G, hwy_speeds=None, fallback=None, precision=1)
ox.speed.add_edge_travel_times(G, precision=1)

def get_distance_cost(G, route):
    route = list(route)
    weight = 0
    for u,v in zip(route[:-1], route[1:]):
        leng = G[u][v][0]['length']
        weight += leng
    return weight
def get_time_cost(G, route):
    route = list(route)
    weight = 0
    for u,v in zip(route[:-1], route[1:]):
        leng = G[u][v][0]['travel_time']
        weight += leng
    return weight

def Dijkstra_fine(G,origin,destination, criteria = 'Distance'):
    # convert map nodes into index from 0 to length(nodes) to simplify our algorithm 
    n = len(G.nodes)
    map_nodes = list(G.nodes)
    # initial defination of the distance list with infinity for all nodes and zero for source node
    dist = [math.inf] * n
    dist[map_nodes.index(origin)] = 0
    # mark all nodes as unvisited 
    visited = [False] * n
    parent  = [None] * n
    while sum(visited) <= n:
        # index of the node of the minimum dist with condition that it is not visited
        current_node = dist.index(min(dist[at] for at in range(len(dist)) if visited[at]==False))
        # here, we will  terminate the searching after reaching the the required destination 
        if current_node == map_nodes.index(destination) :
            break
        # iterate over all neighbors of the current node
        for child in nx.neighbors(G,map_nodes[current_node]):
            # get distance between currrent node and child node
            distance = dist[current_node] + func(G,map_nodes[current_node],child, criteria)
            # update minimum distance if the calculated distnace is less than previous distance
            if distance < dist[map_nodes.index(child)]:
                dist[map_nodes.index(child)] = distance
                parent[map_nodes.index(child)] = current_node
        visited[current_node] = True

    path = []            
    path.append(map_nodes.index(destination))
    while path[-1] != None:
        path.append(parent[path[-1]])
    path.pop()
    path.reverse()
    return [map_nodes[i] for i in path]

def func(G, node1, node2, criteria):
    if criteria =='Distance':
        distance = G[node1][node2][0]['length'] # length between the nodes
    elif criteria == 'Time':
        distance = G[node1][node2][0]['travel_time'] # time between the nodes
    return distance

class Node:
    # using __slots__ for optimization
    __slots__ = ['node', 'distance', 'parent', 'osmid', 'G']
    # constructor for each node
    def __init__(self ,graph , osmid, distance = 0, parent = None):
        # the dictionary of each node as in networkx graph --- still needed for internal usage
        self.node = graph[osmid]
        # the distance from the parent node --- edge length
        self.distance = distance
        # the parent node
        self.parent = parent
        # unique identifier for each node so we don't use the dictionary returned from osmnx
        self.osmid = osmid
        # the graph
        self.G = graph

    def expand(self, criteria):
        children = []
        for child in self.node:
            if criteria == 'Time':
                dist = self.node[child][0]['travel_time']
            elif criteria == 'Distance':
                dist = self.node[child][0]['length']
        
            Node_ = Node(graph = self.G, 
                         osmid = child,
                         distance = dist,
                         parent = self)
            children.append(Node_)
        return children 
    # returns the path from that node to the origin as a list and the length of that path
    def path(self):
        node = self
        path = []
        while node:
            path.append(node.osmid)
            node = node.parent
        return path[::-1]

    def __eq__(self, other):
        try:
            return self.osmid == other.osmid
        except:
            return self.osmid == other
    def __hash__(self):
        return hash(self.osmid)
    
    
def Dijkstra(G,origin,destination,criteria = 'Distance'):
    seen = set()
    shortest_dist = {osmid: math.inf for osmid in G.nodes()}
    unrelaxed_nodes = [Node(graph = G, osmid = osmid) for osmid in G.nodes()]

    shortest_dist[origin.osmid] = 0
    found = False

    while len(unrelaxed_nodes) > 0 and not found:
        node = min(unrelaxed_nodes, key = lambda node : shortest_dist[node.osmid])  

        unrelaxed_nodes.remove(node)
        seen.add(node.osmid)  

        if node == destination:
            route = node.path()
            cost = shortest_dist[node.osmid]
            found = True
            continue
        
        for child in node.expand(criteria):
            if child.osmid in seen:
                continue

            child_obj = next((node for node in unrelaxed_nodes if node.osmid == child.osmid), None)
            child_obj.distance = child.distance
            distance = shortest_dist[node.osmid] + child.distance
            if distance < shortest_dist[child_obj.osmid]:
                shortest_dist[child_obj.osmid] = distance
                child_obj.parent = node
    return route

origin = Node(graph = G, osmid = highlighted[0])
destination = Node(graph = G, osmid = highlighted[1])
route1 = Dijkstra(G, origin, destination, 'Distance')
route2 = Dijkstra(G, origin, destination, 'Time')


origin_node = orig_point
destination_node = dest_point

paths = nx.all_simple_paths(G, origin_node, destination_node)

distance_route1 = round(get_distance_cost(G, route1)/1000, 2)

time_route1 = (round((get_time_cost(G, route1)/ 60), 2))

distance_route2 = round(get_distance_cost(G, route2)/1000, 2)

time_route2 = (round((get_time_cost(G, route2)/ 60), 2))


location_point = lat, long

folium_map = folium.Map(location= location_point,
                        zoom_start=14,
                        tiles="OpenStreetMap")
paths = [route1, route2]
color_list = ['#FF3333', '#0F3FE5']

distR1 = ('Route with Minimum Distance<br>Distance: ' + str(distance_route1)
          + 'meters<br>Time:'+ str(time_route1) + 'minutes')

distR2 = ('Route with Minimum Time<br>Distance: ' + str(distance_route2)
          + 'meters<br>Time:'+ str(time_route2) + 'minutes')

popup1 = folium.Popup(distR1, min_width = 100, max_width = 170)
popup2 = folium.Popup(distR2, min_width = 100, max_width = 170)

path_coordinates1 = []
path_coordinates2 = []
                            
for i in route1:
    path_coordinates1.append([G.nodes[i]['y'],G.nodes[i]['x']])
route1_line = folium.PolyLine(path_coordinates1, color="#008000", weight=4, popup=popup1).add_to(folium_map)

for i in route2:
    path_coordinates2.append([G.nodes[i]['y'],G.nodes[i]['x']])
route2_line = folium.PolyLine(path_coordinates2, color='#002F6C', weight=4, popup=popup2).add_to(folium_map)
    
folium.Marker(location=[G.nodes[highlighted[0]]['y'],
                        G.nodes[highlighted[0]]['x']],
              icon= folium.Icon(color='blue',icon='map-marker'),
              popup = input_origin).add_to(folium_map)

folium.Marker(location=[G.nodes[highlighted[1]]['y'],
                        G.nodes[highlighted[1]]['x']],
              icon= folium.Icon(color='red',icon='map-marker'),
              popup = input_destination).add_to(folium_map)
folium_map.save('Dijkstra.html')