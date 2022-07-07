import time
import random
import bpy

from bpy import context

import numpy as np


def random_route(number_of_points):
    '''Generate a random ordering of indices'''
    return random.sample(range(0, number_of_points), number_of_points)


def calculate_route_length(route, points):
    '''Add up the length of all the edges in the route to get the complete length'''
    distance = 0

    for i in range(len(route) - 1):
        distance += get_distance(route[i], route[(i + 1) % points.shape[0]])
        # distance += np.linalg.norm(points[route[i]] -
        #                            points[route[(i + 1) % points.shape[0]]])

    return distance


def create_edges_from_route(route):
    '''Take a route and return a list of edges for a mesh'''
    edges = []
    for i in range(len(route) - 1):
        edges.append((route[i], route[i+1]))

    edges.append((route[len(route) - 1], route[0]))

    return edges


def create_mesh_from_route(route, vertices):
    '''Create new mesh from edges and route'''

    # Generate the edges
    edges = create_edges_from_route(best_route)

    # Create a new mesh from the edges and vertices
    faces = []
    new_mesh = bpy.data.meshes.new('new_mesh')
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()

    # make object from mesh
    new_object = bpy.data.objects.new('new_object', new_mesh)

    # add object to a scene collection
    context.collection.objects.link(new_object)
    # bpy.data.collections[0].objects.link(new_object)


def swap_2opt(route, point1, point2):
    # Reverse the section indicated by the indices
    new_route = route.copy()
    new_route[(point1 + 1):(point2 + 1)
              ] = route[(point1 + 1):(point2 + 1)][::-1]
    return new_route


def precalculate_distances(points):
    '''Memoizes the distances between all points'''
    global distances

    distances = np.zeros([len(points), len(points)])
    for x in range(len(points)):
        for y in range(len(points)):
            distances[x][y] = np.linalg.norm(points[x] - points[y])


def get_distance(point1, point2):
    '''Retrieves the memoized distance'''

    return distances[point1][point2]

    # Get the active object


# Will hold all the memoized distances
distances = np.zeros(0)

obj = context.active_object
print("current object", obj)

# For the runtime to be calculated
start_time = time.time()


# Get vertices as a list of tuples
vertices = [vert.co for vert in obj.data.vertices]
print(vertices[1])

# Convert vector to np array
points = np.array(vertices)

print(points)

# Cache the distances so they can be reused
precalculate_distances(points)
print("Distances: ", distances)

num_points = points.shape[0]

# Get a random route of the correct size
best_route = random_route(num_points)
print(best_route)

# Loop through until no improvement can be found
# You can replace while loop with a for loop if you only want to iterate a certain number of times
path_improved = True

while (path_improved):
    path_improved = False
    for i in range(0, num_points - 1):
        for j in range(i + 1, num_points):

            original_distance = get_distance(
                best_route[i], best_route[(i + 1) % num_points]) + get_distance(best_route[j], best_route[(j + 1) % num_points])
            swapped_distance = get_distance(
                best_route[i], best_route[j]) + get_distance(best_route[(i + 1) % num_points], best_route[(j + 1) % num_points])

            if (swapped_distance < original_distance):
                best_route = swap_2opt(
                    best_route, i, j)

                path_improved = True

                # Removing this will give a speed up
                print("Updated route", calculate_route_length(
                    best_route, points))
                break
        if path_improved:
            break


print("Final Route", best_route)

create_mesh_from_route(best_route, vertices)

print("--- ran for: %s seconds ---" % (time.time() - start_time))
