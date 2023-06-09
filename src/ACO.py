import osmnx
import networkx
import random
from tqdm.notebook import tqdm
import folium
import matplotlib.pyplot as plt
from time import time
import sqlite3


place = 'Iloilo City, Philippines'
G = osmnx.graph_from_place(place, clean_periphery=True, simplify=True, network_type= 'drive')

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

class Node:
    # using __slots__ for optimization
    __slots__ = ['node', 'distance', 'time','parent', 'osmid', 'G']
    # constructor for each node
    def __init__(self ,graph , osmid, distance = 1, time = 1 ,parent = None):
        # the dictionary of each node as in networkx graph --- still needed for internal usage
        self.node = graph[osmid]
        
        # the distance from the parent node --- edge length
        self.distance = distance
        
        # the parent node
        self.parent = parent
        
        self.time = time
        
        # unique identifier for each node so we don't use the dictionary returned from osmnx
        self.osmid = osmid
        
        # the graph
        self.G = graph
    
    # returning all the nodes adjacent to the node
    def expand(self):
        children = [Node(graph = self.G, osmid = child, distance = self.node[child][0]['length'], parent = self) \
            for child in self.node]
        return children
    
    # returns the path from that node to the origin as a list and the length of that path
    def path(self):
        node = self
        path = []
        while node:
            path.append(node.osmid)
            node = node.parent
        return path[::-1]
    
    # the following two methods are for dictating how comparison works

    def __eq__(self, other):
        try:
            return self.osmid == other.osmid
        except:
            return self.osmid == other
    
    def __hash__(self):
        return hash(self.osmid)
    
lat = Get_LatLong.latitude
long = Get_LatLong.longitude

orig_point = Get_Origin.origin
dest_point = Get_Destination.destination

origin_node = Node(graph=G, osmid=orig_point)
destination_node = Node(graph=G, osmid=dest_point)

highlighted = [orig_point, dest_point]

nc = ['r' if node in highlighted else '#336699' for node in G.nodes()]
ns = [50 if node in highlighted else 8 for node in G.nodes()]


osmnx.speed.add_edge_speeds(G, hwy_speeds=None, fallback=None, precision=1)
osmnx.speed.add_edge_travel_times(G, precision=1)

def cost(G, route):
    weight = 0
    for u, v in zip(route[:-1], route[1:]):
        weight += G[u][v][0]['length']   
    return round(weight, 4)

def get_time_cost(G, route):
    weight = 0
    for u, v in zip(route[:-1], route[1:]):
        weight += G[u][v][0]['travel_time']
    return round (weight, 4)

alpha = 2
beta = 2

n = 500
Q = 1

pheremone_concentrations = dict()
known_routes = dict()

# randomize the pheromones
pheremone_concentrations = {(u,v):random.uniform(0,0.5) for [u,v] in G.edges()}

def pheremone(level, distance, alpha, beta):
    return level ** alpha * ((1/distance)) ** beta

for ant in tqdm(range(n)):
    # Place the ant at the colony
    frontier = [origin_node]
    explored = set()
    route = []
    found = False

    while frontier and not found:
        parent = frontier.pop(0)
        explored.add(parent)

        children = []
        children_pheremones = []
        for child in parent.expand():
            # If we see the destination, ignore all pheremones
            if child == destination_node:
                found = True
                route = child.path()
                continue
            if child not in explored:
                children.append(child)
                children_pheremones.append(
                    pheremone(
                        pheremone_concentrations[(parent.osmid, child.osmid)],
                        child.distance,
                        alpha,
                        beta,
                    )
                )

        if len(children) == 0:
            continue  # The ant is stuck, go back.

        transition_probability = [
            children_pheremones[i] / sum(children_pheremones)
            for i in range(len(children_pheremones))
        ]

        chosen = random.choices(children, weights=transition_probability, k=1)[0]

        # Add all the non-explored children in case we need to explore them later
        children.pop(children.index(chosen))
        frontier.extend(children)

        # Set the chosen child to be the next node to explore
        frontier.insert(0, chosen)

    for u, v in zip(route[:-1], route[1:]):
        length_of_edge = G[u][v][0]['length']
        pheremone_concentrations[(u,v)] += Q/length_of_edge
    
    # If the route is newly discovered, add it to the list
    route = tuple(route)
    if route in known_routes:
        known_routes[route] += 1
    else:
        known_routes[route] = 1

best_route = max(known_routes, key=known_routes.get)
time_used = known_routes[best_route]

time = round((get_time_cost(G, route) / 60), 2)
distance = round((cost(G, route) / 1000), 2)

location_point = lat, long
folium_map = folium.Map(location= location_point,
                        zoom_start=14,
                        tiles="OpenStreetMap")


aco_route = ('Alternative Route<br>Distance: ' + str(distance)
          + 'km<br>Time:'+ str(time) + 'minutes')

popup = folium.Popup(aco_route, min_width = 100, max_width = 170)

path_coordinates = []

for i in route:
    path_coordinates.append([G.nodes[i]['y'],G.nodes[i]['x']])
route_line = folium.PolyLine(path_coordinates, color="#008000", weight=4, popup=popup).add_to(folium_map)
    
folium.Marker(location=[G.nodes[highlighted[0]]['y'],
                        G.nodes[highlighted[0]]['x']],
              icon= folium.Icon(color='blue',icon='map-marker'),
              popup = input_origin).add_to(folium_map)

folium.Marker(location=[G.nodes[highlighted[1]]['y'],
                        G.nodes[highlighted[1]]['x']],
              icon= folium.Icon(color='red',icon='map-marker'),
              popup = input_destination).add_to(folium_map)
folium_map.save('ACO.html')